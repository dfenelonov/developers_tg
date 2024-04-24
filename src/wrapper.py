from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import GigaChat
# Remember to use your own values from my.telegram.org!
api_id = 27661056
api_hash = '05d76b5fcac4ddddfb991156ce033e1a'
import os
from dotenv import load_dotenv
aug_template = 'Девелопер {company} (ИНН застройщика {inn}) Адрес: {text}'

class GigachatWrapper:
    def __init__(self, augmentation_template=aug_template, template="Определи девелоперскую компанию в новости, она должна быть застройщиком. В ответе напиши только её название, если в тексте нет названия девелоперской компании, напиши Нет.\nНовость: {text}"):
        load_dotenv()
        assert (os.environ["GIGACHAT_CREDENTIALS"])
        self.prompt = PromptTemplate.from_template(template)
        self.llm = GigaChat(verify_ssl_certs=False, scope="GIGACHAT_API_CORP")
        self.llm_chain = LLMChain(prompt=self.prompt, llm=self.llm)

    def condense(self, message):
        generated = self.llm_chain.invoke(input={"text": message})
        return generated['text']

    def augmentation(self, inn, company, message):
        return f"{aug_template}".format(company=company, inn=inn, text=message)
