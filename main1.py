import streamlit as st
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import os
import subprocess
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.agents import Tool



def generate_crypto_responses(crypto, start_date, end_date, prompt,key,chat_history):
    # Download the cryptocurrency data
    data = yf.download(crypto, start=start_date, end=end_date)

    # Write data to a CSV file
    data.to_csv(f"{crypto}.csv")
    # Create the Langchain agent
    llm=OpenAI(temperature=0,openai_api_key=key)
    if "memory" not in st.session_state:
                st.session_state.memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                )

    agent = create_csv_agent(
            llm,
            "BTC-USD.csv",
            verbose=True
        )
    


    # Run the agent to generate a response based on the user's prompt
    response = agent.run(prompt)
    chat_history.append((prompt, response))

    return response

def display_chat_history(chat_history):
    
    for i, (question, answer) in enumerate(chat_history):
        st.info(f"Question {i + 1}: {question}")
        st.success(f"Answer {i + 1}: {answer}")
        st.write("----------")


def download_data(crypto, start_date, end_date):
    data = yf.download(crypto, start=start_date, end=end_date)
    data.to_csv(f"{crypto}.csv")
    st.success(f"Data for {crypto} downloaded successfully!")


def main():

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status:
        # Set the title of the Streamlit app
        st.title("Ask Crypto Analytics Question")
        with st.sidebar.expander("API Key Input"):
            with st.form(key="api_form"):
                api_key = st.text_input("Enter your OpenAI API key:", type="password")
                submit_button = st.form_submit_button(label="Submit")

                if submit_button and api_key:
                    # Perform actions using the API key
                    st.success("API key submitted:")
        if api_key:
            # Define the cryptocurrency options
            cryptos = [
                'BTC-USD', 'ETH-USD', 'XRP-USD', 'BCH-USD', 'LTC-USD', 'DOGE-USD',
                'USDT-USD', 'ADA-USD', 'BNB-USD', 'LINK-USD', 'XLM-USD', 'SOL1-USD',
                'THETA-USD', 'ETC-USD', 'FIL-USD', 'TRX-USD', 'EOS-USD', 'XMR-USD',
                'AVAX-USD'
            ]

            # Get user input
            crypto = st.sidebar.selectbox("Select a cryptocurrency", cryptos)
            start_date = st.sidebar.date_input("Select a start date")
            end_date = st.sidebar.date_input("Select an end date")

            
            
            with st.form(key='my_form', clear_on_submit=True):
                
                prompt = st.text_input("Query:", placeholder="Type Your Query (:", key='input')
                submit_button = st.form_submit_button(label='Send',type='primary')
                
            
                # output =
            # prompt = st.text_input("Enter your question or prompt")

          # Add a "Download Data" button
            if st.sidebar.button("Download Data"):
                download_data(crypto, start_date, end_date)
                st.session_state.show_dataframe = True
                st.session_state.show_clear = True * 2

            # Show DataFrame if data is downloaded
            if st.session_state.get("show_dataframe", False):
                data = pd.read_csv(f"{crypto}.csv")
                st.write(data)

                # Add a "Show DataFrame" button
            if st.sidebar.button("Show Data"):
                # Display the DataFrame
                df = pd.read_csv(f"{crypto}.csv")
                st.dataframe(df)
                st.session_state.show_clear = True

            # Generate response based on user input
            if submit_button and prompt:
                response = generate_crypto_responses(crypto, start_date, end_date, prompt,api_key,st.session_state.chat_history)

                # Display the question and response
                st.write(f"Question: {prompt}")
                st.write(f"Answer: {response}")

            # Add a "Clear" button
            if st.session_state.get("show_clear", False):
                if st.sidebar.button("Clear"):
                    st.session_state.show_dataframe = False
                    st.session_state.show_clear = False

            with st.expander("**View Chat History**"):
                    display_chat_history(st.session_state.chat_history)   

    elif authentication_status == False:
        st.error("Username/password is incorrect")

    elif authentication_status == None:
        st.warning("Please enter your username and password")
    else:
        st.error("Authentication failed. Please try again.")


if __name__ == '__main__':
    main()
