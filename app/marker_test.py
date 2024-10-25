from marker.convert import convert_single_pdf
from marker.models import load_all_models

if __name__ == "__main__":
    model_lst = load_all_models()
    full_text, images, out_meta = convert_single_pdf("../examples/example-mri.pdf", model_lst)
    print(full_text)

