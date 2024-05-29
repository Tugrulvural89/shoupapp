from PIL.Image import Image
from django import forms
from .models import Contact
from .models import UploadedImage


class ProductForm(forms.Form):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
        ('de', 'German'),
        ('tr', 'Turkish'),
    ]
    image = forms.ImageField(required=False, label="Upload Image", help_text="Maks Size 50MB - Min pixel 1000 x 1000")
    product_link = forms.URLField(required=False, label="Product Link on Marketplace",
                                  help_text="Product link or image is required")
    title = forms.CharField(max_length=200, required=False, label="Title", help_text="Optional Attribute")
    product_size = forms.CharField(max_length=100, required=False, label="Product Size", help_text="Optional Attribute")
    product_color = forms.CharField(max_length=100, required=False, label="Product Color",
                                    help_text="Optional Attribute")
    description = forms.CharField(widget=forms.Textarea, required=False, label="Additional Information",
                                  help_text="Optional Attribute")
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, label="Language",
                                 help_text="Select the language for the description")
    category = forms.CharField(max_length=100, required=False, label="Product Category", help_text="Optional Attribute")

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image:
            if image.size > 50 * 1024 * 1024:  # 50 MB
                raise forms.ValidationError("The image file size must be under 50 MB.")

            img = Image.open(image)
            if img.width < 1000 or img.height < 1000:
                raise forms.ValidationError("The image resolution must be at least 1000x1000 pixels.")

        return image

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        product_link = cleaned_data.get("product_link")

        if not image and not product_link:
            raise forms.ValidationError("Either upload an image or provide a product link.")
        return cleaned_data


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'content']
