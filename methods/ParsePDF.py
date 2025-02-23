from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import elements_to_json

class ExtractFromPDF:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract(self):
        elements = partition_pdf(
            filename=self.file_path,
            include_page_breaks=True,
            strategy="hi_res",
            infer_table_structure=True,
            extract_element_types=["Table"],
            max_characters=None,
            languages=["eng"],
            hi_res_model_name="yolox",
        )

        data = dict()
        for i, e in enumerate(elements):
            if str(e) == "NAMED INSURED’S FULL NAME":
                data["name"] = str(elements[i + 1])
            if str(e) == "PHYSICAL ADDRESS OF THE INSURED PROPERTY":
                data["address"] = str(elements[i + 1])

        return data