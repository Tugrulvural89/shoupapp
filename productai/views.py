import base64

from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

from .forms import ProductForm
from django.http import HttpResponse

from .forms import ContactForm
from .models import Contact, CustomPage, Blog, UploadedImage
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .utils import scrape_product_info
from openai import OpenAI
from decouple import config


def run_openai_model(content=None, image_file_base=None, product_size=None, product_color=None, description=None,
                     title=None, language=None, category=None):
    api_Key = config('OPENAI_API_KEY')
    content_list_one = config('CONTENT_LIST_ONE')
    content_list_two = config('CONTENT_LIST_TWO')
    content_list_three = config('CONTENT_LIST_THREE')
    content_list_four = config('CONTENT_LIST_FOUR')
    content_list_five = config('CONTENT_LIST_FIVE')
    content_list_six = config('CONTENT_LIST_SIX')
    content_list_seven = config('CONTENT_LIST_SEVEN')
    content_list_eight = config('CONTENT_LIST_EIGHT')

    client = OpenAI(api_key=api_Key)
    messages_list = []
    result_text = 'Not Available Now'
    if content != 'Not Available' and content is not None:
        content_list = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_one
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_two
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_three
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_four
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_five
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_six
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_seven
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "user content is " + str(content)
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_eight
                    }
                ]
            },
        ]
        messages_list = content_list
    elif image_file_base:
        # if image_file_base is existing
        image_list = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_one
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_two
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "use product img into content. product image is" + image_file_base
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_four
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_five
                    }
                ]
            },

            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_six
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_seven
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_file_base
                        }
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": content_list_eight
                    }
                ]
            },
        ]
        messages_list = image_list
        if len(title) > 2:
            my_title_dict = {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": title
                    }
                ]
            }
            messages_list.append(my_title_dict)
        if len(product_color) > 2:
            color_dict = {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": product_color
                    }
                ]
            }
            messages_list.append(color_dict)
        if len(description) > 2:
            description_dict = {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": description
                    }
                ]
            }
            messages_list.append(description_dict)
        if len(category) > 2:
            category_dict = {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "product will be listing in " + category
                    }
                ]
            }
            messages_list.append(category_dict)
        if len(language) > 2:
            language_dict = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "content text language must be in " + language
                    }
                ]
            }
            messages_list.append(language_dict)
        if len(product_size) > 2:
            size_dict = {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": product_size
                    }
                ]
            }
            messages_list.append(size_dict)

    else:
        result_text = 'Not Available Now'
    print(messages_list)
    if len(messages_list) > 0:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages_list,
            temperature=1,
            max_tokens=4095,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        try:
            result_text = response.choices[0].message.content
        except:
            result_text = 'Not Available Now'
    return result_text


def index(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            print("form is ")
            # image = form.cleaned_data.get('image')
            # product_link = form.cleaned_data.get('product_link')
            title = form.cleaned_data.get('title')
            product_size = form.cleaned_data.get('product_size')
            product_color = form.cleaned_data.get('product_color')
            description = form.cleaned_data.get('description')
            image_file = form.cleaned_data['image']
            inputs = form.cleaned_data.get('product_link')
            category = form.cleaned_data.get('category')
            language = form.cleaned_data.get('language')
            # if image upload
            if image_file:
                uploaded_image = UploadedImage(image=image_file)
                uploaded_image.save()
                # Resmin URL'sini elde et

                image_url = request.build_absolute_uri(uploaded_image.image.url)

                response_text = run_openai_model(image_file_base=image_url, title=title,
                                                 description=description,
                                                 product_size=product_size,
                                                 product_color=product_color, language=language, category=category)

            # if url input exist
            elif 'https://' in inputs and image_file is None:
                # content parser
                try:
                    content = scrape_product_info(inputs)
                    # live link if available
                    response_text = run_openai_model(content)
                # if raise error bs4
                except:
                    response_text = "Not Available"
            else:
                response_text = "Not Available"

            return render(request, 'index.html', {'form': form, 'content': response_text})
    else:
        form = ProductForm()
    return render(request, 'index.html', {'form': form})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! We will reach out to you as soon as possible.")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def custom_page(request, slug=None):
    content = get_object_or_404(CustomPage, slug=slug)
    return render(request, 'custom.html', {'content': content})


def blog(request):
    blog_list = Blog.objects.all().order_by('-publish')  # Assuming there's a date_posted field
    paginator = Paginator(blog_list, 10)  # Show 10 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog.html', {'page_obj': page_obj})


def blog_detail(request, slug=None):
    blogDetail = get_object_or_404(Blog, slug=slug)
    return render(request, 'blog_detail.html', {'post': blogDetail})


def privacy(request):
    return render(request, 'privacy.html', {})


def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /admin/",
        "Allow: /",
        "Sitemap: https://www.shoupapp.com/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
