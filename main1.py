import streamlit as st
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from IPython.display import display, Markdown
import os


def generate_crypto_responses(crypto, start_date, end_date, prompt):
    # Download the cryptocurrency data
    data = yf.download(crypto, start=start_date, end=end_date)
    
    # Write data to a CSV file
    data.to_csv(f"{crypto}.csv")

    # Create the Langchain agent
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
    agent = create_csv_agent(
        OpenAI(temperature=0),
        f"{crypto}.csv",
        verbose=True
    )

    # Run the agent to generate a response based on the user's prompt
    response = agent.run(prompt)

    return response


def download_data(crypto, start_date, end_date):
    data = yf.download(crypto, start=start_date, end=end_date)
    data.to_csv(f"{crypto}.csv")
    st.success(f"Data for {crypto} downloaded successfully!")


def main():
    # Set the title of the Streamlit app
    st.title("Ask Crypto Analytics Question")

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
    prompt = st.text_input("Enter your question or prompt")

    # Add a "Download Data" button
    if st.sidebar.button("Download Data"):
        download_data(crypto, start_date, end_date)

    # Generate response based on user input
    if prompt:
        response = generate_crypto_responses(crypto, start_date, end_date, prompt)

        # Display the question and response
        st.write(f"Question: {prompt}")
        st.write(f"Answer: {response}")

if __name__ == '__main__':
    main()
