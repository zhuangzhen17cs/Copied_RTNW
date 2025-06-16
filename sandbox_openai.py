import pandas as pd
import json
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
import sys
import os


# Setting up environment
sys.path.insert(0, os.path.abspath('..'))
from config import set_environment
set_environment()

#Initialize LLM
llm = ChatOpenAI(model_name='gpt-4-0613')

def load_data(csv_path, json_path):
    df = pd.read_csv(csv_path)
    with open(json_path, 'r') as f:
        articles_data = json.load(f)
    return df, articles_data

def get_articles_for_category(category, df, articles_data):
    category_urls = df[df['Product Category'].str.lower() == category.lower()]['Product url'].tolist()
    related_articles = []
    for article in articles_data:
        if any(url in article.get('link', '') for url in category_urls) or \
           category.lower() in article.get('text', '').lower():
            related_articles.append(article)
    return related_articles

def generate_product_summary(category, related_articles):
    # Prepare article texts
    article_texts = []
    for article in related_articles[:3]:
        if article.get('text'):
            article_texts.append(f"Title: {article.get('title', 'N/A')}\nContent: {article['text'][:700]}...")
    combined_articles = "\n\n".join(article_texts)
    # Create the prompt template
    template = ChatPromptTemplate.from_messages([
        ('system', '''You are an expert technical writer specializing in electronic components and products. 
        Create a comprehensive summary that includes 2 paragraphs:
        1. 2-3 lines about what the product category is, how it is used, and why it is popular. Preferably add information about the product category from DigiKey.com
        2. 2-3 lines summarizing key insights from the provided articles. If no key insights are provided from articles then provide your own insights and do not mention that articles have no specific insights.
        Keep the summary concise, informative, and technical but accessible.'''),
        ('user', '''Product Category: {category}
        Related Articles:
        {articles}
        Please provide a summary following the specified format.''')
    ])
    
    chain = template | llm | StrOutputParser()
    summary = chain.invoke({
        "category": category,
        "articles": combined_articles if combined_articles else "No specific articles found for this category."
    })
    return summary

def search_product_category(category):
    csv_path = './intermediate_data/Product_Article_Matching.csv'
    json_path = './intermediate_data/Cleaned_Article_Data.json'
    try:
        df, articles_data = load_data(csv_path, json_path)
        related_articles = get_articles_for_category(category, df, articles_data)
        summary = generate_product_summary(category, related_articles)
        return summary
    except Exception as e:
        return {
            'category': category,
            'summary': f"No category found",
        }