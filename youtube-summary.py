import streamlit as st
import validators
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader,UnstructuredURLLoader
from PIL import Image
from pytube.innertube import InnerTube
from innertube import _default_clients

# original_init = InnerTube.__init__

# Define a new init method that sets 'WEB' as the default client
# def new_init(self, client='WEB', *args, **kwargs):
#     original_init(self, client=client, *args, **kwargs)
    
# # Replace the original init method with the new one
# InnerTube.__init__ = new_init

_default_clients['ANDROID_MUSIC']['context'] = _default_clients['WEB']['context']
_default_clients['ANDROID_MUSIC']['header'] = _default_clients['WEB']['header']
_default_clients['ANDROID_MUSIC']['api_key'] = _default_clients['WEB']['api_key']

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')

st.set_page_config(page_title='Summarizer')

img1 = Image.open('youtubeLogo.jpg')

img2 = Image.open('web.jpeg')

col1,col2,col3 = st.columns([1,1,3])

with col1:
    st.image(img1,use_column_width=True)

with col2:
    st.image(img2,use_column_width=True)

with col3:
    st.title('Summarize Youtube Videos / Web Page')


llm = ChatGroq(model='Gemma2-9b-It',groq_api_key=groq_api_key)


system_prompt = '''
Summarize the content from given {text} in best possible way.
'''

prompt = PromptTemplate(
    input_variables=['text'],
    template=system_prompt
)

system_prompt_n = '''
You are an advanced AI summarization tool.Your task is to extract the key points, themes, and essential information from various online content, 
and give the final summary from {text}.
Analyze the content, focusing on the following criteria:
1.Main Ideas: Identify the primary arguments or messages conveyed in the content.
2.Supporting Details: Highlight important examples, statistics, or pieces of evidence that reinforce the main ideas.
3.Structure: Maintain the original flow of the content, summarizing it in a coherent manner that mirrors the order of presented information.
4.Length: Produce a summary that is concise.
5.Clarity and Readability: Ensure the summary is written in clear, simple language that is easy to understand, avoiding difficult words unless necessary.
6.Contextual Relevance: Tailor the summary based on the intended audience, making sure it is appropriate for their level of understanding and interest.
'''

final_prompt = PromptTemplate(
    input_variables=['text'],
    template=system_prompt_n
)

URL = st.text_input(label='Paste URL here',placeholder='https://www.youtube.com/')

if st.button('Summarize the Video/Web-page'):
    if not URL:
        st.info('Please provide the url')
    
    elif not validators.url(URL):
        st.warning('Please provide the correct url')

    else:
        try:
            with st.spinner('Summarizing...'):
                if 'youtube.com' in URL or 'youtu.be' in URL:
                    loader = YoutubeLoader.from_youtube_url(URL,add_video_info=True,language=['en-IN','hi','en'])
                else:
                    loader = UnstructuredURLLoader([URL],ssl_verify=False,mode='single',
                                                   headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 BingBot/2.0'})

                docs = loader.load()

                chain = load_summarize_chain(llm,chain_type='map_reduce',
                                             map_prompt=prompt,
                                             combine_prompt=final_prompt)
                
                response = chain.run(docs)

                st.success(response)

        except Exception as e:
            st.exception(f'Exception : {e}')
