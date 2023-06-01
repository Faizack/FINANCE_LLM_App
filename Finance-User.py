import streamlit as st
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
import os
from IPython.display import Markdown, display
from openai.error import AuthenticationError,RateLimitError
from sklearn.linear_model import LinearRegression

def list_files_in_folder(folder_path):
    files = os.listdir(folder_path)
    return files

def generate_crypto_responses(crypto, start_date, end_date, prompt, key, chat_history, offline_data,selectedfile):
    if offline_data:
        # Load data from the offline file
        data = pd.read_csv(f"Offline-Data/{selectedfile}")
    else:
        # Download the cryptocurrency data
        data = yf.download(crypto, start=start_date, end=end_date)

        # Write data to a CSV file
        data.to_csv(f"Online-Data/{crypto}.csv")

    # Create the Langchain agent
    llm = OpenAI(temperature=0, openai_api_key=key)
    agent = create_csv_agent(
        llm,
        f"Offline-Data/{selectedfile}" if offline_data else f"Online-Data/{crypto}.csv",
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
    data.to_csv(f"Online-Data/{crypto}.csv")
    st.success(f"Data for {crypto} downloaded successfully!")

def main():
    st.title("Finlyzr: AI-Powered Financial Data Assistant")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []


    if 'show_dataframe' not in st.session_state:
        st.session_state.show_dataframe = False


    with st.sidebar.expander("API Key Input"):
        with st.form(key="api_form"):
            api_key = st.text_input("Enter your OpenAI API key:", type="password")
            submit_button = st.form_submit_button(label="Submit")

            if submit_button and api_key:
                # Perform actions using the API key
                st.success("API key submitted:")

    if api_key:
        try:
            # Define the cryptocurrency options
            cryptos = [
                'BTC-USD', 'ETH-USD', 'XRP-USD', 'BCH-USD', 'LTC-USD', 'DOGE-USD',
                'USDT-USD', 'ADA-USD', 'BNB-USD', 'LINK-USD', 'XLM-USD', 'SOL1-USD',
                'THETA-USD', 'ETC-USD', 'FIL-USD', 'TRX-USD', 'EOS-USD', 'XMR-USD',
                'AVAX-USD'
            ]

            with st.sidebar.expander("Data Source"):
                data_source = st.radio("Select Data Source:", ("Online Data", "Offline Data"))
                offline_data = True if data_source == "Offline Data" else False

            if offline_data:
                with st.sidebar.expander("Fetech Offline Data"):
                    folder_paths = '/home/developer/faijan/GenCode/gen-Code/Generative-App/Offline-Data/'
                    files = list_files_in_folder(folder_paths)
                    selectedfile = st.selectbox("Select a file", files)
                    st.write("You selected this file:", selectedfile)
            else:
                selectedfile = None

            with st.sidebar.expander("Fetch Online Data"):
                # Get user input
                crypto = st.selectbox("Select a cryptocurrency", cryptos)
                start_date = st.date_input("Select a start date")
                end_date = st.date_input("Select an end date")

                # Add a "Download Data" button
                if st.button("Download Data"):
                    download_data(crypto, start_date, end_date)
                    st.session_state.show_dataframe = True
                    st.session_state.show_clear = True * 2

            st.session_state.show_clear = True

            if st.session_state.get("show_clear", False):
                if st.sidebar.button("Clear"):
                    st.session_state.show_dataframe = False
                    st.session_state.show_clear = False

            if st.session_state.show_dataframe:
                if offline_data and selectedfile:
                    # Display offline data
                    df = pd.read_csv(f"Offline-Data/{selectedfile}")
                else:
                    # Display online data
                    df = pd.read_csv(f"Online-Data/{crypto}.csv")
                st.dataframe(df)

            with st.form(key='my_form', clear_on_submit=True):
                prompt = st.text_input("Query:", placeholder="Type your query", key='input')
                submit_button = st.form_submit_button(label='Send', type='primary')

            if submit_button and prompt:
                response = generate_crypto_responses(crypto, start_date, end_date, prompt, api_key,
                                                    st.session_state.chat_history, offline_data, selectedfile )

                # Display the question and response
                st.write(f"Question: {prompt}")
                st.write(f"Answer: {response}")

                if st.sidebar.button("Show Data"):
                    try :
                        if offline_data and selectedfile:
                            # Display offline data
                            df = pd.read_csv(f"Offline-Data/{selectedfile}")
                        else:
                            # Display online data
                            df = pd.read_csv(f"Online-Data/{crypto}.csv")
                        st.dataframe(df)
                    except :
                        st.sidebar.warning(f"Please Download {crypto} data")

            with st.expander("**View Chat History**"):
                display_chat_history(st.session_state.chat_history)

            if st.button("Clear Chat History"):
                st.session_state['chat_history'] = []

        except AuthenticationError as e :
            link = "[Click here](https://platform.openai.com/account/api-keys)"
            st.error(f"Ensure the API key used is correct, clear your browser cache, or generate a new one {link}")

    else:
        st.warning("Please add an API key")


if __name__ == '__main__':
    main()
