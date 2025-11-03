import io
import os
from base64 import b64encode

from openai import OpenAI
from pdf2image import convert_from_path

from lib.promt_manager import PromptManager


class LLMClient:
    def __init__(
        self, api_key: str, api_base: str, ai_model: str, prompts_dir: str = "prompts"
    ):
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        self.ai_model = ai_model
        self.prompt_manager = PromptManager(prompts_dir)

    def convert_to_base64(self, file_path: str) -> str:
        """
        Convert a file to a base64 encoded string. If it's a PDF, convert to JPEG image first.

        :param file_path: Path to the file to be converted (PDF/PNG/JPEG).
        :return: Base64 encoded string of the file (as JPEG).
        """
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == ".pdf":
            # Convert PDF to image (first page only)
            try:
                images = convert_from_path(file_path, first_page=1, last_page=1)
                if not images:
                    raise ValueError("PDF conversion failed: No pages found")
                # Convert PIL image to JPEG bytes
                img = images[0]
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format="JPEG")
                img_byte_arr = img_byte_arr.getvalue()
                return b64encode(img_byte_arr).decode("utf-8")
            except Exception as e:
                raise ValueError(f"Error converting PDF to image: {str(e)}")
        else:
            # Handle image files (PNG/JPEG) as before
            with open(file_path, "rb") as f:
                return b64encode(f.read()).decode("utf-8")

    def identify_components(
        self, image_path: str, analysis_mode: str = "default", **prompt_kwargs
    ):
        """
        Identify electrical components in single-line diagrams using the LLM API.

        :param image_path: Path to the electrical diagram image file (PDF/PNG/JPEG).
        :param analysis_mode: Analysis mode from config (default, power_quality, etc.)
        :param prompt_kwargs: Additional variables for prompt customization
        :return: JSON string of identified electrical components with specifications.
        """
        base64_image = self.convert_to_base64(image_path)

        # Load prompts using the prompt manager
        system_prompt = self.prompt_manager.load_system_prompt()
        user_prompt = self.prompt_manager.render_component_analysis_prompt(
            analysis_mode, **prompt_kwargs
        )

        response = self.client.chat.completions.create(
            model=self.ai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
        )
        return response.choices[0].message.content

    def clean_json_response(self, response_text: str) -> str:
        """
        Clean the JSON response by removing markdown formatting.

        :param response_text: Raw response text that may contain ```json formatting
        :return: Clean JSON string
        """
        # Remove ```json at the beginning
        if response_text.strip().startswith("```json"):
            response_text = response_text.strip()[7:]  # Remove ```json
        elif response_text.strip().startswith("```"):
            response_text = response_text.strip()[3:]  # Remove ```

        # Remove ``` at the end
        if response_text.strip().endswith("```"):
            response_text = response_text.strip()[:-3]  # Remove trailing ```

        return response_text.strip()

    def parse_components_for_bom(self, components_json: str):
        """
        Parse the identified components and format them for Bill of Materials.

        :param components_json: JSON string from identify_components method
        :return: Formatted list suitable for BOM generation
        """
        import json

        try:
            # Clean the JSON response first
            clean_json = self.clean_json_response(components_json)
            components = json.loads(clean_json)
            bom_items = []

            for component in components:
                bom_item = {
                    "Item": component.get("name", "Unknown"),
                    "Description": f"{component.get('type', 'Component')} - {component.get('rating', 'N/A')}",
                    "Voltage_Rating": component.get("voltage", "N/A"),
                    "Current_Rating": component.get("rating", "N/A"),
                    "Quantity": component.get("quantity", 1),
                    "Specifications": component.get("specifications", "Standard"),
                    "Unit": "Each",
                }
                bom_items.append(bom_item)

            return bom_items
        except json.JSONDecodeError:
            print("Error: Could not parse components JSON")
            return []

    def generate_bom_summary(
        self, image_path: str, analysis_mode: str = "default", **prompt_kwargs
    ):
        """
        Complete workflow: Identify components and format for BOM.

        :param image_path: Path to the electrical diagram
        :param analysis_mode: Analysis mode from config (default, power_quality, etc.)
        :param prompt_kwargs: Additional variables for prompt customization
        :return: Dictionary with components and BOM data
        """
        components_json = self.identify_components(
            image_path, analysis_mode, **prompt_kwargs
        )
        # Clean the JSON response before processing
        clean_json = self.clean_json_response(components_json)
        bom_items = self.parse_components_for_bom(clean_json)

        return {
            "raw_analysis": clean_json,
            "bom_items": bom_items,
            "total_items": len(bom_items),
            "analysis_mode": analysis_mode,
        }
