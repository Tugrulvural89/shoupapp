import os
from PIL import Image
import pillow_heif
from django import forms
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.forms.fields import FileField
from .models import Contact, UploadedImage

pillow_heif.register_heif_opener()


class HEICFileField(FileField):
    def validate(self, value):
        if value is not None:
            ext = os.path.splitext(value.name)[1].lower()
            allowed_extensions = [
                '.bmp', '.dib', '.gif', '.jfif', '.jpe', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.pnm', '.pfm', '.png',
                '.apng', '.blp', '.bufr', '.cur', '.pcx', '.dcx', '.dds', '.ps', '.eps', '.fit', '.fits', '.fli', '.flc',
                '.ftc', '.ftu', '.gbr', '.grib', '.h5', '.hdf', '.jp2', '.j2k', '.jpc', '.jpf', '.jpx', '.j2c', '.icns',
                '.ico', '.im', '.iim', '.mpg', '.mpeg', '.tif', '.tiff', '.mpo', '.msp', '.palm', '.pcd', '.pdf', '.pxr',
                '.psd', '.qoi', '.bw', '.rgb', '.rgba', '.sgi', '.ras', '.tga', '.icb', '.vda', '.vst', '.webp', '.wmf',
                '.emf', '.xbm', '.xpm', '.heic'
            ]
            if ext not in allowed_extensions:
                raise ValidationError(f"File extension '{ext}' is not allowed. Allowed extensions are: {', '.join(allowed_extensions)}.")
            super().validate(value)

class ProductForm(forms.Form):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
        ('de', 'German'),
        ('tr', 'Turkish'),
    ]
    image = HEICFileField(required=False, label="Upload Image", help_text="Max Size 50MB - Min pixel 500 x 500")
    product_link = forms.URLField(required=False, label="Product Link on Marketplace", help_text="Product link or image is required")
    title = forms.CharField(max_length=200, required=False, label="Title", help_text="Optional Attribute")
    product_size = forms.CharField(max_length=100, required=False, label="Product Size", help_text="Optional Attribute")
    product_color = forms.CharField(max_length=100, required=False, label="Product Color", help_text="Optional Attribute")
    description = forms.CharField(widget=forms.Textarea, required=False, label="Additional Information", help_text="Optional Attribute")
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, label="Language", help_text="Select the language for the description")
    category = forms.CharField(max_length=100, required=False, label="Product Category", help_text="Optional Attribute")

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image:

            try:
                # Convert HEIC to PNG if necessary
                ext = os.path.splitext(image.name)[1].lower()
                if ext == '.heic':
                    try:
                        image.seek(0)
                        img = Image.open(image)
                    except Exception as e:
                        raise forms.ValidationError(f"Invalid HEIC image file: {str(e)}")
                else:
                    img = Image.open(image)
                    img.verify()  # Verify that it is an image
                    img = Image.open(image)  # Re-open the image after verify

                # Resize the image initially to speed up processing
                img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)

                # Convert to PNG
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)

                # Check the file size after conversion
                if buffer.getbuffer().nbytes > 20 * 1024 * 1024:  # 20 MB
                    # Resize the image to reduce the file size
                    while buffer.getbuffer().nbytes > 20 * 1024 * 1024:  # 20 MB
                        width, height = img.size
                        img = img.resize((width // 2, height // 2), Image.Resampling.LANCZOS)
                        buffer = BytesIO()
                        img.save(buffer, format="PNG")
                        buffer.seek(0)

                # Create a new InMemoryUploadedFile to replace the original image
                converted_image = InMemoryUploadedFile(
                    buffer,
                    'ImageField',
                    f"{image.name.split('.')[0]}.png",
                    'image/png',
                    buffer.getbuffer().nbytes,
                    None
                )

                return converted_image
            except (IOError, SyntaxError, ValidationError) as e:
                raise forms.ValidationError(f"Invalid image file: {str(e)}")
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
