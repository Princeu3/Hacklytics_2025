import os
from typing import Dict, List, Any
from groq import Groq
from Judge import process_files

class FraudAnalyzer:
    def __init__(self, groq_api_key: str):
        """Initialize the fraud analyzer with Groq API key."""
        self.client = Groq(api_key=groq_api_key)
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
                        
                        Consider the following factors:
                        1. Consistency between satellite imagery and reported damage
                        2. Timeline consistency across all evidence
                        3. Metadata validation from images/videos
                        4. Severity of damage correlation across different sources
                        5. Weather data correlation with claimed damage
                        6. Pattern recognition from historical claims
                        
                        Provide your analysis in the following format:
                        - Fraud Probability Score (0-100)
                        - Risk Level (Low/Medium/High)
                        - Key Findings (bullet points)
                        - Red Flags (if any)
                        - Recommendations for Further Investigation
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
                "key_findings": [],
                "red_flags": [],
                "recommendations": []
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
        probability_match = re.search(r'(?i)probability.*?(\d+)', analysis)
        probability = int(probability_match.group(1)) if probability_match else None
        
        # Extract risk level
        risk_match = re.search(r'(?i)risk.*?(low|medium|high)', analysis)
        risk_level = risk_match.group(1).capitalize() if risk_match else None
        
        # Extract key findings
        findings = []
        red_flags = []
        recommendations = []
        
        current_section = None
        for line in analysis.split('\n'):
            line = line.strip()
            if 'key findings' in line.lower():
                current_section = 'findings'
            elif 'red flags' in line.lower():
                current_section = 'flags'
            elif 'recommendations' in line.lower():
                current_section = 'recommendations'
            elif line.startswith('-') or line.startswith('•'):
                if current_section == 'findings':
                    findings.append(line.lstrip('- •').strip())
                elif current_section == 'flags':
                    red_flags.append(line.lstrip('- •').strip())
                elif current_section == 'recommendations':
                    recommendations.append(line.lstrip('- •').strip())
        
        return {
            "fraud_probability": probability,
            "risk_level": risk_level,
            "key_findings": findings,
            "red_flags": red_flags,
            "recommendations": recommendations,
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
    GROQ_API_KEY = "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"
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
    
    print("\nKey Findings:")
    for finding in fraud_assessment['key_findings']:
        print(f"- {finding}")
    
    print("\nRed Flags:")
    for flag in fraud_assessment['red_flags']:
        print(f"- {flag}")
    
    print("\nRecommendations:")
    for rec in fraud_assessment['recommendations']:
        print(f"- {rec}") 