####------ import packages 

# General
import pandas as pd
import streamlit as st
import numpy as np
import pandas as pd

# Image preprocessing
import cv2
import numpy as np

# OCR 
import pytesseract
from PIL import Image

# AWS
import boto3

# Path stuff
from pathlib import Path


S3_BUCKET_NAME = 'saracapstone'
s3 = boto3.client('s3')

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=st.secrets['S3_KEY'],
                      aws_secret_access_key=st.secrets['S3_SECRET'])

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False

#-------------- Home page ------- DONE



# Sidebar options
with st.sidebar:
    st.header("""Main Menu""")

page = st.sidebar.selectbox("", ["🏠 Home", "📜 Upload and convert", "📂 Add to repository", "👀 About this project", "❓ FAQ"])
st.sidebar.markdown("""---""")
st.sidebar.write('Get in touch via my [LinkedIn profile](www.linkedin.com/in/sara-jabbar)')



##------------- streamlit pages (HOME) ------- DONE



if page == "🏠 Home":
# set page background
    def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://saracapstone.s3.amazonaws.com/homepage.jpg");
                background-attachment: fixed;
                background-size: cover
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    add_bg_from_url()

# homepage text
    # Set intro text
    st.title('Kurdish Manuscript Digitalization tool (Soranî)')
    st.header('بە خێر بێن | bi xêr bên')
    st.write('This online tool allows the user to convert any Kurdish images containing text, into a digitized text document using a retrained Google Tesseract OCR engine.')
    st.write('In addition, authorized researchers can browse through Zheen Archive Center\'s repository and request access to documents relevant to their research topic.')
    #st.write('_A collaboration with the [Zheen Archive Center](https://zheen.org/en/home/)_')
    st.markdown("""
    """, unsafe_allow_html=True)
    st.markdown("""
    <br>
    """, unsafe_allow_html=True)

# add "partners/affiliates"
    col1, col2, col3, col4 = st.columns([1, 3, 3, 1]) # HYPERLINK ALL PAGES
    with col1:
        st.write(' ')
    with col2:
        st.image('https://saracapstone.s3.amazonaws.com/zheen+logo.png')
        st.caption('[In collaboration with Zheen Archive Center](https://zheen.org/en/home/)')
    with col3:
        st.image('https://saracapstone.s3.amazonaws.com/tesseract.png')
        st.caption('This tool is built & trained with Tesseract')
    with col4: 
        st.write(' ')
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1: 
        st.write(' ')
    with col2:
        st.image('https://saracapstone.s3.amazonaws.com/MSBA+logo.png')
        st.caption('     Powered by MSBA at the American University of Beirut')
    with col3:
        st.write(' ')



##------------- streamlit pages (OCR)



elif page == '📜 Upload and convert':
    # set page background
    def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://saracapstone.s3.amazonaws.com/conversion+page.png");
                background-attachment: fixed;
                background-size: cover
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    add_bg_from_url()
    st.title('OCR Tool for Kurdish (Soranî)')
    st.write('-----')
    # upload files
    st.header('Step 1: Upload your document(s)')
    st.write('Start converting by uploading your document(s) below:')

    st.markdown("""
    <br>
    """, unsafe_allow_html=True)

    # file uploader # 1
    uploaded_file = st.file_uploader("📃 Upload one image file", type=['png', 'jpg', 'tif'])
    
    st.markdown("""
    <br>
    """, unsafe_allow_html=True)
    # Preprocessing image(s)
    st.write('---------')
    st.header('Step 2: Modify & preprocess your image(s)')
    st.subheader('Read the following steps before converting:')
    st.write('Please note that accuracy levels depend on the overall quality of the image')
    st.write('If your image is rotated, please make sure to correctly rotate it before uploading')
    st.write('OCR engines are typically designed to detect text that has previously been typed. If your document contain handwritten text, the overall conversion won\'t be as accurate. A dpi of > 300 is recommended')
    st.write('[sample with high accuracy](https://media.fontsgeek.com/generated/e/l/elektra-text-pro-regular-sample.png)   |   [sample with low accuracy](http://www.saradistribution.com/foto4/dokan2.jpg)')


#-------------- OCR ENGINE PREPROCESSING (BEGINNING)
#-------------- back-end (START)--------------------------#



    st.write('-------')

    # 1. Regular photo
    @st.cache
    def load_image(uploaded_file):
        image = Image.open(uploaded_file)
        return image
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.write(' ')
    with col2:
        if uploaded_file is not None:
            img = load_image(uploaded_file)
            st.image(load_image(uploaded_file), caption = 'Original photo')
        else:
            st.write(' ')
    with col3:
        st.write(' ')

    st.write('------------')

    # 2. Inverted 
    col1, col2 = st.columns(2)
    try:
        img_file = np.array(img) # convert to numpy array
    except:
        st.error("Please upload a picture to get started")
        st.stop()

    inverted_image = cv2.bitwise_not(np.array(img))

    with col1:
        st.image(inverted_image, caption = 'Inverted photo (JPEG compatible only)')

    # 3. Grayscale 
    def grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = grayscale(np.array(img))
    with col2:
        st.image(gray_image, 'Grayscale photo')

    # 4. Binarization & watermark removal 
    col1, col2 = st.columns(2)
    thresh, im_bw = cv2.threshold(np.array(img), 190, 250, cv2.THRESH_BINARY) # would be nice if they can adjust threshold themselves
    with col1:
        st.image(grayscale(im_bw), caption = 'Black & white photo')

    # 5. Noise removal 
    def noise_removal(image):
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        image = cv2.medianBlur(image, 3)
        return(image)
    no_noise = noise_removal(grayscale(im_bw)) # would be nice if they can adjust noise levels themselves
    with col2:
        st.image(no_noise, caption = 'No noise')

    # 6. Thick/erosion 
    col1, col2 = st.columns(2)
    def thin_font(image):
        image = cv2.bitwise_not(image)
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)
        image = cv2.bitwise_not(image)
        return(image)
    eroded_image = thin_font(no_noise)
    with col1:
        st.image(eroded_image, caption = 'Thinner text')

    # 7. Thin/dilation 
    def thick_font(image):
        image = cv2.bitwise_not(image)
        kernel = np.ones((3, 3), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        image = cv2.bitwise_not(image)
        return(image)
    dilated_image = thick_font(no_noise)
    with col2:
        st.image(dilated_image, caption = 'Thicker text')

    # 8. Skewed/rotated 
    # Calculate skew angle of an image
    def getSkewAngle(cvImage) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
        newImage = cvImage.copy()
        gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
        dilate = cv2.dilate(thresh, kernel, iterations=5)

    # Find all contours
        contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)

    # Find largest contour and surround in min area box
        largestContour = contours[0]
        minAreaRect = cv2.minAreaRect(largestContour)

    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
        angle = minAreaRect[-1]
        if angle < -45:
            angle = 90 + angle
        return -1.0 * angle

    # Rotate the image around its center
    def rotateImage(cvImage, angle: float):
        newImage = cvImage.copy()
        (h, w) = newImage.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return newImage

    def deskew(cvImage):
        angle = getSkewAngle(cvImage)
        return rotateImage(cvImage, 0 * angle) # -1.0 is another option if it's actually skewed
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.write(' ')
    with col2:
        fixed = deskew(im_bw)
        st.image(fixed, caption = 'Deskewed text')
    with col3:
        st.write(' ')



#-------------- back-end (END)--------------------------#



    st.write('--------')
    st.header('Step 3: Choose your edited image')
    st.write('**Please select the photo that looks the most \'accurate\'.**')
    st.write('_Usually, the thicker the text, and the cleaner the background, the better it is for the OCR engine to predict each and every character_')
    option = st.selectbox('',('Original photo', 'Inverted photo', 'Grayscale photo', 'Black & white photo', 'No noise', 'Thinner text', 'Thicker text', 'Deskewed text'))
    
    # Select the most accurate photo as the photo of choice
    if option == 'Original photo':
        selected_image = img
    elif option == 'Inverted photo':
        selected_image = inverted_image
    elif option == 'Grayscale photo':
        selected_image = gray_image
    elif option == 'Black & white photo':
        selected_image = im_bw
    elif option == 'No noise':
        selected_image = no_noise
    elif option == 'Thinner text':
        selected_image = eroded_image
    elif option == 'Thicker text':
        selected_image = dilated_image
    elif option == 'Deskewed text':
        selected_image = fixed

    # Conversion (OCR)
    st.write('-----------')
    st.header('Step 3: Convert!')
    st.write('**If your document contains more than one language, please check the box that applies:**')

    home_dir = Path.home()
    tess_path = Path('/Users/sarajabbar/Desktop/trainingtesseract/tesseract/tessdata')

    tessdata_dir_config = r'--tessdata-dir "/Users/sarajabbar/Desktop/trainingtesseract/tesseract/tessdata"'
    
    lang1 = r'-l fas+ckbLayer'
    lang2 = r'l ara+ckbLayer+sarchia'
    lang3 = r'l ara+ckbLayer'

    persian = st.checkbox('Persian')
    arabic = st.checkbox('Arabic')
    normal = st.checkbox('Just Kurdish (Soranî)')
    if persian:
        lang = lang1
    elif arabic:
        lang = lang2
    else:
        lang = lang3 # default

    ocr_result = pytesseract.image_to_string(selected_image, lang=lang, config = tessdata_dir_config)
    if st.button('View raw text'):
        st.write(ocr_result)
    st.download_button(label="Download data as a text file", data=ocr_result, file_name='converted.txt', mime='text')

    # Explanatory text
    st.write('--------')
    st.write('_If you\'re still unhappy with the results, please get in touch with me through the "contact me" page accessible via the sidebar to explore further options._')



##------------- streamlit pages (ADD TO REPOSITORY) ------- DONE



elif page == "📂 Add to repository": 
    # set page background
    def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://saracapstone.s3.amazonaws.com/repository+page.png");
                background-attachment: fixed;
                background-size: cover
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    add_bg_from_url()

    st.title('Add your document to our e-repository')
    st.write('Part of preserving history is making sure that it is available, accessible and shareable for the public to use.')
    st.write('If you would like to build or add to this e-repository of Kurdish manuscripts, please fill out the form below and upload the converted document(s), along with the respective image(s).')

    # submit doc
    with st.form('Add document to repository'):
        st.write('Main information (required)')
        document_title = st.text_input('Document title')
        document_description = st.text_input('Document description')
        document = st.file_uploader('Upload your text or doc file here')

        submitted_1 = st.form_submit_button('Submit')
        # save document
        if document is not None:
            stringio = document.getvalue().decode("utf-8")
            #st.write(stringio)
            title = [document_title]
            desc = [document_description]
            text = [stringio]
            text = pd.DataFrame({'title': title, 'text': text, 'description': desc})
            text.to_csv('text.csv')
        else:
            st.write(' ')

        if submitted_1:
            #textdoc = stringio.write('doc.txt')
            uploaded = upload_to_aws('text.csv','manuscriptrepository', 'doc.csv')
            st.success('Thank you for contributing to our e-repository!')
        else:
            st.write(' ')

    # submit image
    with st.form('Add image to repository'):
        document_original = st.file_uploader('Upload the scanned version of the document here')
        submitted_2 = st.form_submit_button('Submit image')

        @st.cache
        def load_image(uploaded_file):
            image = Image.open(uploaded_file)
            return image

        # save image
        if document_original is not None:
            img = load_image(document_original)
            saved_img = img.save('saved_img.jpg')
        else:
            st.write(' ')

        if submitted_2: 
            uploaded_2 = upload_to_aws('saved_img.jpg', 'saracapstone', 'saved_img.jpg')
            st.success('Thank you for contributing to our e-repository!')
        else:
            st.write(' ')

###### note: bucket versioning on AWS is enabled to store all files under the same file name



##------------- streamlit pages (ABOUT) ------- DONE 



elif page == "👀 About this project":
    # set page background
    def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://saracapstone.s3.amazonaws.com/about+page.png");
                background-attachment: fixed;
                background-size: cover
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    add_bg_from_url()
    # Project intro text
    st.title('The motivation behind this project')
    st.write('---------')
    st.write('This project is submitted in partial fulfillment of the requirements of the MSBA program at the American University of Beirut.')
    st.write('After discussing some capstone project ideas with a friend of mine, who coincidentally is embarking on a PhD journey in Kurdish Studies in the UK, we started talking about the challenges he faced gaining access to documents that are relevant to his research. He mentioned that while Zheen contains a plethora of useful documents, the only way he can access them is by visiting the center physically, speaking to the center founders, and obtaining relevant documents, journals, books and manuscripts, is by handing them a USB drive that would eventually contain scanned images of these historic documents.')
    st.write('While I applaud Zheen\'s openness to helping young researchers, especially considering the fact that they\'re an independent not-for-profit entity, I started wondering if I, an aspiring data scientist, can perhaps help them digitalize their document retrieval system.')
    st.write('As a result, and after obtaining helpful data from Zheen, I was able to train an open source OCR/LSTM engine to convert images to text by using their Arabic trained data to produce a Kurdish conversion tool that would preprocess any images to improve the OCR\'s output quality, while also allowing Zheen to store output on a repository for researchers to access.')
    st.write('While the process has not been easy, especially for a less resourced language like Kurdish, I\'m confident that this tool will pave the way for future Kurdish data scientists to use their skills to support and strengthen the presence of the Kurdish language.')
    st.write('The source code for the project can be accessed through the \'contact me\' button at the end of this page')
        # ADD MORE TEXT BASED ON YOUR REPORT

# supplemental text
    st.write('-------')
    st.subheader('The hidden issue at hand')
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write('The Kurdish Language, while widely used today by more than 30 million people, is still considered a less resourced language. With that being said, a lot of \'shortcuts\' can be used by exploiting similar languages\' script, such as Arabic and Farsi.')
        st.write('While we are witnessing a cultural transformation in the Kurdistan Region of Iraq, one cannot help but think of the decline in the usage of the Kurdish language. Kurdish youth opt for speaking, writing, and reading in English, as opposed to Kurdish. Stores on the street no longer opt for Kurdish signs, but would rather appeal to potentail customers with English signages because using words that are not colliquial in nature are not easily comprehensible by the masses.')
    with col2:
        st.image('https://images.unsplash.com/photo-1564181878-744b50a5da7a?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=870&q=80', 
        caption='A gentleman reading a paper on Mawlawi Street. Photo by Dastan Khdir on Unsplash') # HYPERLINK IF POSSIBLE
    
    st.write('-------')
    st.subheader('The value of our language')
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write('Where do we go from here? Well, for starters, a lot of work is required to ensure the digitization of an entire culture. Whether that\'s by making Kurdish literary sources more accessible to the masses through technology, or by digitizing business, governmental, healthcare and educational processes without leaving Kurdish out.')
        st.write('These steps, albeit small, should trickle down slowly and become part of a Kurdish person\'s identity.')
    with col2:
        st.image('https://images.unsplash.com/photo-1590222772565-74d949c57242?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1548&q=80', 
        caption='A statue of Mahwi, a prominent Kurdish poet. Photo by Salman Majeed on Unsplash') # HYPERLINK IF POSSIBLE
    
    st.write('-------')
    st.subheader('The future of the Kurdish Language')
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write('That being said, digitization is key. While we are witnessing a technological transformation, primarily led by the KRG, more should be done to several sectors, all while aiming to be as inclusive as possible. Many Kurdish citizens speak little to no English or Arabic. We should ensure that with the digital transformation comes a certain responsibility to make these tools as available to the public as possible.')
    with col2:
        st.image('https://images.unsplash.com/photo-1644718847149-69be6cee8dd2?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=928&q=80', 
        caption='A young boy taking home some "samoon hajari". Photo by Levi Meir Clancy on Unsplash') # HYPERLINK IF POSSIBLE

    st.write('------')
    st.subheader('Special thanks')
    st.write('I could not have even thought this project through without the help of my professors, program coordinator, advisor, and peers at the Olayan School of Business at [American University of Beirut](aub.edu.lb). While challenging, I am so grateful for the new skills I\'ve attained throughout this program. I am confident that this is only the beginning, and will continue to build on the knowledge I\'ve gained through further professional and academic development.')
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        st.write(' ')
    with col2:
        st.image('https://saracapstone.s3.amazonaws.com/AUB+logo.png')
    with col3:
        st.write(' ')



##------------- streamlit pages (FAQ) ------- DONE 



elif page == "❓ FAQ":
    # set page background
    def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://saracapstone.s3.amazonaws.com/FAQ+page.png");
                background-attachment: fixed;
                background-size: cover
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    add_bg_from_url()
    st.title('Frequently Asked Questions')
    st.write('------')
    st.subheader('_How does [Tesseract](https://tesseract-ocr.github.io) work?_')
    st.write('Tesseract is an OCR engine that was initially built in the 1980\'s by Hewlett-Packard in the 1980\'s. It has since been sponsored by Google, and is an open-source software that consists of two engines- an LSTM (a form of Artificial Recurrent Neural Network), as well as a Legacy Engine. It uses training data, as well as script, font, and unicharset files to classify characters and words through deep learning. It can either be used directly via the command line, or can be embedded onto an API.')
    st.write('It can also be retrained using different fonts, new languages and characters, as well as by adding different language combinations, page segmentations, tables, and other page formats.')
    st.write('--------')
    st.subheader('_How does preprocessing an image improve its accuracy?_')
    st.write('Since Tesseract allows raw images to be inputted, image distortions can weaken the accuracy of the result. As such, different preprocessing techniques can be applied to reduce inaccuracies, such as the removal of noise, color pigmentation, watermarks, skewing, and shadows')
    st.write('_[What is noise?](https://tesseract-ocr.github.io/tessdoc/images/noise.png)_')
    st.write('_[What is a negative/inverted photo?](https://i0.wp.com/css-tricks.com/wp-content/uploads/2020/06/bkg-fixed-3.png?resize=1137%2C1374&ssl=1)_')
    st.write('_[What is a watermark?](https://eshop.macsales.com/blog/wp-content/uploads/2019/02/Screen-Shot-2019-02-13-at-9.20.28-AM.png)_')
    st.write('_[What is considered "not aligned"?](https://tesseract-ocr.github.io/tessdoc/images/skew-linedetection.png)_')
    st.write('--------')
    st.subheader('_How can I train my own Tesseract model?_')
    st.write('Tesseract\'s documentation lists the different ways in which a new model can be trained. Refer to the [linked](https://github.com/tesseract-ocr/tesstrain) GitHub page to follow the steps necessary.')
    st.write('--------')
    st.subheader('_Why is my output inaccurate?_')
    st.write('Because this tool was trained specifically for the Kurdish language (with the exception of embedded Persian and Arabic language options), your document might contain characters that might not get recognized due to the trained model\'s language configuration. In addition, the image you are converting might not be as accurate or clear, making it difficult for the OCR tool to characterize the letter._')
    st.write('---------')
    st.write('_If you would like to collaborate on developing a new OCR tool using a different language, please click on the LinkedIn profile on the sidebar to get in touch and discuss new opportunities._')
