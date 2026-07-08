## Language
- For Windows  
extract Packages\gettext0.20.2-iconv1.16-static-64.zip to C:\>Tools\Gettext
Add C:\>Tools\Gettext\bin to system environment path

- For Debian


# Update Table (Drop Table Method)
## 1. Export Data from Workbench (Data Only)
## 2. Update exported data
## 3. Drop Table from database
## 4. Update Drop Table status in Django
./manage.py migrate --fake <tablename> zero
## 5. Recreate Table
./manage.py migrate
## 6. Import Data from Workbench (Data Only) 

# Visual Studio Code with Django
install packages:
pylint
pylint-django
autopep8

{
    "python.pythonPath": "/usr/local/bin/python3",
    "python.venvPath": "/Volumes/Data/Workspace/Django/venv/",
    "python.linting.pylintArgs": ["--load-plugins", "pylint_django"],
}

# GeoDjango
## Packages
Geopy   get coordinate according the address and reverse geocode

## OpenStreetMap Reference - Django-leaflet
https://github.com/makinacorpus/django-leaflet
http://blog.mathieu-leplatre.info/geodjango-maps-with-leaflet.html
https://fle.github.io/easy-webmapping-with-django-leaflet-and-django-geojson.html
https://maptimeboston.github.io/leaflet-intro/

## Install GDAL for GeoDjango, for Django 2.1, use GDAL 2.3.1 above.
$ wget http://download.osgeo.org/gdal/1.11.5/gdal-1.11.5.tar.gz
$ tar xzf gdal-1.11.5.tar.gz
$ cd gdal-1.11.5

$ ./configure
$ make # Go get some coffee, this takes a while.
$ sudo make install
$ cd ..

## Install GDAL in Debian
$ sudo apt-get install binutils libproj-dev gdal-bin

## Vector Tile
https://github.com/tilezen/vector-datasource


# Google Recaptcha
https://www.google.com/recaptcha/

## Bootstrap Select
[Bootstrap](https://github.com/silviomoreto/bootstrap-select)

### Drop  ###CountryPicker use BootStrap Select 
https://www.jqueryscript.net/form/Bootstrap-Country-Picker-jQuery.html
1. Load the necessary jQuery, Bootstrap and Bootstrap Select plugin in the html document.
<!-- Stylesheet -->
<link rel="stylesheet" href="/path/to/bootstrap.min.css">
<link rel="stylesheet" href="/path/to/bootstrap-select.min.css">

<!-- JavaScript -->
<script src="/path/to/jquery.min.js"></script>
<script src="/path/to/bootstrap.min.js"></script>
<script src="/path/to/bootstrap-select.min.js"></script>

2. Download and load the jQuery countryPicker.js script after jQuery library.
<script src="js/countrypicker.js"></script>

3. Create a default country picker from a normal select element.
<select class="selectpicker countrypicker">
</select>

4. Enable the live search functionality.
<select class="selectpicker countrypicker"
        data-live-search="true">
</select>

5. Set the pre-selected country.
<select class="selectpicker countrypicker"
        data-live-search="true"
        data-default="United States">
</select>

6. Display country flags.
<select class="selectpicker countrypicker"
        data-live-search="true"
        data-default="United States"
        data-flag="true">
</select>

## Bootstrap DatePicker
[DatePicker](https://github.com/uxsolutions/bootstrap-datepicker)

## Flagstrap (Can't select by keybord)
[Flagstrap](https://github.com/blazeworx/flagstrap)

## django-jsignature
[django-jsignature](https://github.com/fle/django-jsignature)


Modify widgets js
./.venv/lib/python3.x/site-packages/jsignature/templates/widgets.py
class="btn" -> class="btn btn-default"

./.venv/lib/python3.x/site-packages/jsignature/widgets.py
#    class Media:
#        js = ('site/js/signature/jSignature.min.js',
#              'site/js/signature/django_jsignature.js')

./venv/lib/python3.x/site-packages/jsignature/settings.py
JSIGNATURE_COLOR = getattr(
    settings, 'JSIGNATURE_COLOR', '#000')
JSIGNATURE_DECOR_COLOR = getattr(
    settings, 'JSIGNATURE_DECOR_COLOR', '#888')

# Multiple Files Upload use Jquery-File-Upload - v9.28.0
# JavaScript-Canvas-to-Blob - v3.14.0
https://github.com/blueimp/jQuery-File-Upload
https://github.com/blueimp/jQuery-File-Upload/wiki/Options#maxnumberoffiles
https://simpleisbetterthancomplex.com/tutorial/2016/11/22/django-multiple-file-upload-using-ajax.html
https://github.com/sibtc/multiple-file-upload

# Blueimp Javascript Load Image - V2.20.1
https://github.com/blueimp/JavaScript-Load-Image
CDN:
https://cdnjs.com/libraries/blueimp-load-image

# Compress Javascript
## Can't use min.js in Django Template, because it can't translate the alert message
https://jscompress.com/
https://javascript-minifier.com/


# Blueimp Gallery - Popup Image Gallery - v2.33.0
https://github.com/blueimp/Gallery

# For PDF XFA Form
Remove XFA PDF Passoword Security Protection
https://smallpdf.com/unlock-pdf

# PDF with AcroForm (pdftk, fdfgen), For IMM5746
1. Export form field from PDF, 
   $pdftk abc.pdf dump_data_fields
2. Use fdfgen create data.fdf base on the input data
3. use pdftk combine data.fdf and PDF
   $pdftk abc.pdf fill_form data.fdf output new.pdf
3. Use pdf2image Convert PDF to image and use Pillow output image back to PDF
    #PIL save multiple page pdf  
    in /venv/lib/pythonxx/sitepackage/PIL/PdfImagePlugin.py
         for append_im in append_images:
             if append_im.mode != im.mode:    
                 append_im = append_im.convert(im.mode)
-                append_im.encoderinfo = im.encoderinfo.copy()
+            append_im.encoderinfo = im.encoderinfo.copy()
             ims.append(append_im)
     numberOfPages = 0
     for im in ims:

## Pillow 5.1.0
    # For Pillow 5.1.0
    88      for append_im in append_images:
    89 +        if append_im.mode != im.mode:
    90 +            append_im = append_im.convert(im.mode)
    91          append_im.encoderinfo = im.encoderinfo.copy()

# PDF with XFA Form (iTextPDF Java), For IMM5709 etc. which require XFA
1. Use iTextPDF export PDF data to XFA XML file
2. Use iTextPDF import data.xml to PDF
3. Usage: java -jar fill5709.jar source.pdf data.xml destination.pdf

# Celery with Amazon SQS
On Worker Server
$ celery worker --app tasks --loglevel=info

Dependcy:
boto3
pycrul

# Check pycurl depends
$ sudo apt-cache depends python-pycurl      
$ sudo apt install libcurl4-gnutls-dev libgnutls28-dev

@app.task(bind=True, default_retry_delay=300, max_retries=5)
def my_task_A():
    try:
        print("doing stuff here...")
    except SomeNetworkException as e:
        print("maybe do some clenup here....")
        self.retry(e)


# Django Database Backup and Restore
django-dbbackup>=3.2.0
python-gnupg                # If need Encrypt the backupfile
$ python manage.py listbackups
$ gzip -d [backupfile.gz]           # Decompress gz file before restore

## Database
$ python manage.py dbbackup -z[--compress]
$ python manage.py dbrestore -z | -i[--input-filename]

## Media
$ python manage.py mediabackup -z[--compress]
$ python manage.py mediarestore -z | -i[--input-filename]


# Letsencrypt SSL certificate
0 3 * * * /usr/bin/certbot renew --post-hook "systemctl reload nginx"

# Clean Logs
* 1 * * * /usr/bin/find /var/log/ -name '*.gz' -mtime +7 -exec rm -f {} \;
* 1 * * * /usr/bin/find /home/admin/Backup/ -name '*.gz' -mtime +7 -exec rm -f {} \;
* 1 * * * /usr/bin/find /home/admin/Backup/ -name '*.xz' -mtime +7 -exec rm -f {} \;
* * 1 * * cat /dev/null > /var/log/celery/celery.service_worker.log
* * 1 * * cat /dev/null > /home/admin/Rentbnb/logs/project.log

# Get CIC Processing Times
0 3 * * * /home/admin/venv/bin/python /home/admin/Rentbnb/src/Rentbnb/processing_times.py

# Backup
0 2 * * * /home/admin/Rentbnb/scripts/backup.sh


# Django Auto Translate
Use custom version 20180318
django-autotranslate>=1.0.2
$ python manage.py makemessages -a
$ python manage.py translate_messages -u
$ python manage.py compilemessages


# WeChatPy
https://github.com/jxtech/wechatpy


# ChatterBot
https://github.com/gunthercox/ChatterBot


# django-private-storage
https://github.com/edoburu/django-private-storage

# Amazon AWS Service and Permission
Resource Group:
    Rentbnb-Production-ResourceGroup
    Rentbnb-Dev-ResourceGroup
    With Key:
        Rentbnb-Production:
        Rentbnb-Dev:
SQS:
    Rentbnb-Production-SQS
    Rentbnb-Dev-SQS

User Group:
    Rentbnb-Production-UserGroup
    Rentbnb-Dev-UserGroup

User:
    Rentbnb-Production-SQS-User
    Rentbnb-Dev-SQS-User




# Google Maps Geocoding API
https://console.developers.google.com/
https://www.scrapehero.com/how-to-parse-unstructured-addresses-using-python-and-google-geocoding-api/


# Selenium
## XPath
//button[contains(@class, 'phoneNumberContainer')]


# Regex
https://regex101.com/


# Bootstrap-Slider
https://github.com/seiyria/bootstrap-slider



# Encrypt and Decrypt ID
https://hashids.org/



# Google Analysis
https://analytics.google.com/analytics/web/

# SEO
https://neilpatel.com/ubersuggest/
Meta tags
<meta name="description" content="A good summary about your page.">
Title
<title>Content Title</title>
Sitemap (Django)
ping_google()

## Key words
canada rental property
property review
tenant review
landord review