import streamlit as st
import validators
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate,MessagesPlaceholder
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader,UnstructuredURLLoader
from PIL import Image
from langchain_core.output_parsers import StrOutputParser
from pytube.innertube import InnerTube
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain.agents import create_openai_tools_agent,AgentExecutor


load_dotenv()

original_init = InnerTube.__init__

# Define a new init method that sets 'WEB' as the default client
def new_init(self, client='WEB', *args, **kwargs):
    original_init(self, client=client, *args, **kwargs)

# Replace the original init method with the new one
InnerTube.__init__ = new_init

# api keys
groq_api_key = os.getenv('GROQ_API_KEY')

# tool
api_wrapper = DuckDuckGoSearchAPIWrapper(max_results=3,safesearch='none')
tool = DuckDuckGoSearchRun(api_wrapper=api_wrapper)

# app 
img1 = Image.open(r'D:\UDEMY\GenAI\Langchain\Text Summarization\youtubeLogo.jpg')

img2 = Image.open(r'D:\UDEMY\GenAI\Langchain\Text Summarization\web.jpeg')

st.set_page_config(page_title='Summarizer')

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
You are an advanced AI summarization tool .Summarize the {text} in the best possible way.
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

lyrics_prompt = '''
You're a skilled data retrieval assistant with expertise in extracting and processing information from various online sources, 
especially youtube videos. Your focus is on accurately identifying and presenting song lyrics as well as the 
artist of the song,singer of the song ,the lable company and the song writer from {text}, 
ensuring clarity and precision in the output.Your task is to fetch the lyrics and singer,artist,label and song writer from the {text} 
generated from a YouTube link of a music video.Don't provide lyrics in paragraph form, provide line by line with proper spacing.

Keep in mind that you should provide the lyrics in the {language} without any additional commentary or unrelated information.
'''

lyrics_template = PromptTemplate(
    input_variables=['text','language'],
    template=lyrics_prompt
)

tool_sys_prompt = '''
you are helpful assistant capable of providing full lyrics in poem format as well as singer,artist,label 
and writer of the {song} in {language}.
'''

# Tools and agent
tool_template = ChatPromptTemplate([
    ('system',tool_sys_prompt),
    MessagesPlaceholder('chat_history',optional=True),
    ('user','{song}'),
    ('user','{language}'),
    MessagesPlaceholder('agent_scratchpad')
])

agent = create_openai_tools_agent(llm=llm,tools=[tool],prompt=tool_template)

executor = AgentExecutor(agent=agent,tools=[tool],verbose=False)

# url loader and text extractor function
def loadAndExtract():
    if 'youtube.com' in URL or 'youtu.be' in URL:
        loader = YoutubeLoader.from_youtube_url(URL,add_video_info=True,language=['en-IN','hi','en'],)
    else:
        loader = UnstructuredURLLoader([URL],ssl_verify=False,mode='single',
                                    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 BingBot/2.0'})

    txt = loader.load()

    return txt

# main app content

URL = st.text_input(label=':blue[**Paste URL here**]',placeholder='https://www.youtube.com/')

option = [':orange[**Select**]',':orange[**English**]',':orange[**Hindi**]']

if "button_pressed" not in st.session_state:
    st.session_state.button_pressed = None

if st.sidebar.button('Previous'):
    st.session_state.button_pressed = None                   # Reset state when pressing 'Previous'
    st.rerun()

if st.session_state.button_pressed != 2:
    if st.button('Summarize the Video/Web-page'):
        st.session_state.button_pressed = 1

if st.session_state.button_pressed != 1:
    if st.button('Provide Lyrics of the song'):
        st.session_state.button_pressed = 2
    selected_option = st.radio(label=':blue[**Select any one language for lyrics**]',options=option)

if st.session_state.button_pressed == 1:    
    if not URL:
        st.info('Please provide the url')
    
    elif not validators.url(URL):
        st.warning('Please provide the correct url')

    else:
        try:
            with st.spinner(':pink[summarizing]'):

                txt = loadAndExtract()

                chain = load_summarize_chain(llm,chain_type='map_reduce',
                                            map_prompt=prompt,
                                            combine_prompt=final_prompt)
                
                response = chain.run(txt)

                st.success(response)

        except Exception as e:
            st.exception(f'Exception : {e}')


elif st.session_state.button_pressed == 2:
    
    if not URL:
        st.info('Please provide the url')
    
    elif not validators.url(URL):
        st.warning('Please provide the correct url')

    else:
        try:
            if 'youtube.com' in URL or 'youtu.be' in URL:
                loader = YoutubeLoader.from_youtube_url(URL,add_video_info=True,language=['en-IN','hi','en'],)
            
                txt = loader.load()

                if txt == []:
                    user_input = st.text_input(label='Plz provide name of the song')
                    if user_input:
                        with st.spinner(':pink[lyrics on the way]'):
                            if option.index(selected_option) == 1:
                                language = 'english'
                            elif option.index(selected_option) == 2:
                                language = 'hindi'
                        
                        res = executor.invoke({'song':user_input,'language':language})

                        st.success(res)

                else:
                    chain = lyrics_template|llm|StrOutputParser()

                    with st.spinner(':pink[lyrics on the way]'):
                        if option.index(selected_option) == 1:
                            language = 'english'
                            res = chain.invoke({'text':txt,'language':language})
                            st.success(res)
                        elif option.index(selected_option) == 2:
                            language = 'hindi'
                            res = chain.invoke({'text':txt,'language':language})
                            st.success(res)
        
        except Exception as e:
            st.exception(f'Exception {e}')
