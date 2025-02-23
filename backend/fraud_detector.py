import os
from typing import Dict, List, Any
from groq import Groq
from backend.Judge import process_files

class FraudAnalyzer:
    def __init__(self, groq_api_key: str):
        """Initialize the fraud analyzer with Groq API key."""
        self.client = Groq(api_key="")
        self.model = "llama-3.3-70b-versatile"

    def analyze_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze claim data for potential fraud using Groq LLM."""
        
        print("\n📋 Creating analysis prompt...")
        prompt = self._create_analysis_prompt(claim_data)
        print("✅ Prompt created")
        print(prompt)
        
        
        try:
            print("\n🤖 Calling Groq API for analysis...")
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert insurance fraud investigator with decades of experience. 
                        Analyze the provided insurance claim data and determine if there are signs of fraud.
                        
                        Apply these specific fraud detection rules:
                        1. Location Consistency:
                           - For photo submissions: metadata addresses must match the form address
                           - For video submissions: metadata addresses shouldn't be accounted for.
                           - If multiple media files exist, all addresses must match closely with zip code.
                           - Mismatched addresses strongly indicate fraud 
                           - If the address is not found in the metadata, Maximum 5 points will be deducted for both Image and Video.
                        
                        2. Structural Damage Verification:
                           - Compare reported external damage against satellite imagery
                           - Major discrepancies between reported and visible damage indicate potential fraud
                        
                        3. Damage Description Consistency:
                           - Compare form descriptions with visual evidence in photos/videos
                           - Inconsistencies in damage descriptions suggest fraudulent activity
                        
                        4. Temporal Analysis:
                           - Media metadata dates must be within 2 weeks of reported incident date
                           - Dates outside this window flag the claim as potentially invalid
                           - Media dates preceding the incident date strongly indicate fraud
                        
                        Provide your analysis in the following format:
                        
                        Fraud Probability Score: [0-100]
                        Risk Level: [Low/Medium/High]
                        Analysis Summary: [Provide a concise explanation of why you believe this claim is or is not fraudulent, 
                        citing specific evidence from the data provided. Focus on the most important discrepancies or validating factors.]
                        
                        For the Fraud Probability Score:
                        - Address mismatches: +30-50 points
                        - Satellite imagery contradictions: +20-40 points
                        - Damage description inconsistencies: +15-30 points
                        - Date discrepancies >2 weeks: +10-20 points
                        - Media dates before incident: +40-60 points
                        """
                    },
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1
            )
            
            analysis = chat_completion.choices[0].message.content
            print("✅ Received analysis from Groq")
            
            print("\n🔍 Parsing analysis results...")
            parsed_results = self._parse_analysis(analysis)
            print("✅ Analysis parsed successfully")
            
            return parsed_results
            
        except Exception as e:
            return {
                "error": str(e),
                "fraud_probability": None,
                "risk_level": None,
                "analysis_summary": None,
                "raw_analysis": None
            }

    def _create_analysis_prompt(self, claim_data: Dict[str, Any]) -> str:
        """Create a detailed prompt from the claim data."""
        
        # Extract relevant information from claim data
        pdf_data = self._extract_pdf_data(claim_data)
        satellite_data = self._extract_satellite_data(claim_data)
        media_data = self._extract_media_data(claim_data)
        
        prompt = f"""
        Please analyze this insurance claim for potential fraud:

        CLAIM DETAILS:
        --------------
        Date of Loss: {pdf_data.get('date_of_loss')}
        Type of Loss: {pdf_data.get('type_of_loss')}
        Description: {pdf_data.get('loss_description')}
        Address: {pdf_data.get('physical_address')}
        
        REPORTED DAMAGES:
        ----------------
        {pdf_data.get('damages_list')}
        
        SATELLITE IMAGERY ANALYSIS:
        -------------------------
        {satellite_data}
        
        PHOTO/VIDEO EVIDENCE:
        -------------------
        {media_data}
        
        Please provide a comprehensive fraud analysis based on these details.
        """
        
        return prompt

    def _extract_pdf_data(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant data from PDF analysis results."""
        pdf_results = {}
        for result in claim_data:
            if result.get('file_type') == 'pdf':
                pdf_results = result.get('analysis_results', {})
                break
        return pdf_results

    def _extract_satellite_data(self, claim_data: Dict[str, Any]) -> str:
        """Extract and format satellite analysis data."""
        for result in claim_data:
            if result.get('file_type') == 'pdf':
                satellite_analysis = result.get('analysis_results', {}).get('satellite_analysis', {})
                if satellite_analysis:
                    return str(satellite_analysis)
        return "No satellite data available"

    def _extract_media_data(self, claim_data: Dict[str, Any]) -> str:
        """Extract and format image/video analysis data."""
        media_findings = []
        for result in claim_data:
            if result.get('file_type') in ['image', 'video']:
                analysis = result.get('analysis_results', {})
                metadata = result.get('metadata', {})
                media_findings.append(f"File: {result['filename']}\n"
                                   f"Analysis: {analysis}\n"
                                   f"Metadata: {metadata}")
        
        return "\n\n".join(media_findings) if media_findings else "No media data available"

    def _parse_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data."""
        import re
        
        # Extract probability score
        probability_match = re.search(r'(?i)fraud probability.*?(\d+)', analysis)
        probability = int(probability_match.group(1)) if probability_match else None
        
        # Extract risk level
        risk_match = re.search(r'(?i)risk level.*?(low|medium|high)', analysis, re.IGNORECASE)
        risk_level = risk_match.group(1).capitalize() if risk_match else None
        
        # Extract analysis summary
        summary_match = re.search(r'(?i)analysis summary:?(.*?)(?=\n\n|$)', analysis, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else None
        
        return {
            "fraud_probability": probability,
            "risk_level": risk_level,
            "analysis_summary": summary,
            "raw_analysis": analysis
        }

def analyze_insurance_claim(folder_path: str, api_key: str) -> Dict[str, Any]:
    """Analyze insurance claim files and detect potential fraud."""
    try:
        print("\n📁 Processing files in folder:", folder_path)
        # Process all files in the folder
        claim_results = process_files(folder_path, api_key)
        print("✅ File processing complete")
        
        print("\n🔎 Initializing fraud analyzer...")
        # Initialize fraud analyzer
        analyzer = FraudAnalyzer(api_key)
        print("✅ Fraud analyzer initialized")
        
        # Perform fraud analysis
        print("\n🧐 Performing fraud analysis...")
        fraud_assessment = analyzer.analyze_claim(claim_results)
        print("✅ Fraud analysis complete")
        
        # Combine results
        final_results = {
            "claim_processing_results": claim_results,
            "fraud_assessment": fraud_assessment
        }
        
        return final_results
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Configuration
    GROQ_API_KEY = "api_key"
    FOLDER_PATH = "./Images and Videos"
    
    # Ensure folder exists
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)
        print(f"Created directory: {FOLDER_PATH}")
        print("Please put your files in this directory and run the script again")
        exit(0)
    
    # Process and analyze claim
    results = analyze_insurance_claim(FOLDER_PATH, GROQ_API_KEY)
    
    # Print results
    print("\n" + "="*50)
    print("FRAUD ANALYSIS RESULTS")
    print("="*50)
    
    fraud_assessment = results["fraud_assessment"]
    print(f"\nFraud Probability: {fraud_assessment['fraud_probability']}%")
    print(f"Risk Level: {fraud_assessment['risk_level']}")
    
    print("\nAnalysis Summary:")
    print(f"- {fraud_assessment['analysis_summary']}")
    
    print("\nRaw Analysis:")
    print(f"- {fraud_assessment['raw_analysis']}") 