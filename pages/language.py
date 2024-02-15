import json
import requests


import streamlit as st
from annotated_text import annotated_text



class CotohaInterface():


    
    def __init__(self, cotoha_info, itit_with_token=True):
        self.cotoha_info = cotoha_info
        self.acces_token_url = cotoha_info["access_token_url"]
        self.base_url = cotoha_info["base_url"]
        self.client_id = cotoha_info["client_id"]
        self.client_secret = cotoha_info["client_secret"]
        
        if itit_with_token:
            self.fetch_access_token()
    
    
    def fetch_access_token(self):
        """ アクセストークンの取得
        """
        url = self.acces_token_url
        headers = {
            "Content-Type": "application/json;charset=UTF-8"
        }
        data = {
            "grantType": "client_credentials",
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        self.access_token_response = json.loads(response.content)
        self.access_token = self.access_token_response["access_token"]
        
        self.common_headers = headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": f"Bearer {self.access_token}"
        }


    
    def parse(self, sentence, type="default"):
        url = self.base_url + "/nlp/v1/parse"
        headers = self.common_headers
        data = {"sentence": sentence, "type":type}
        response = requests.post(url, data=json.dumps(data), headers=headers)
    
        return json.loads(response.content)


    def keyword(self, document, type="default", do_segment=False, max_keyword_num=5):
        url = self.base_url + "/nlp/v1/keyword"
        headers = self.common_headers
        data = {"document":document, "type":type, do_segment:str(do_segment).lower(), "max_keyword_num":max_keyword_num}
        response = requests.post(url, data=json.dumps(data), headers=headers)
    
        return json.loads(response.content)
   
    




@st.cache_data
def init_cotoha():
    cotoha_info = json.loads(st.secrets["cotoha"])
    cotoha = CotohaInterface(cotoha_info)
    return cotoha


@st.cache_data
def parse(sentence, _cotoha, type="default"):
    return _cotoha.parse(sentence,type = type)

@st.cache_data
def keyword(document, _cotoha, **kwargs):
    return _cotoha.keyword(document, **kwargs)





st.markdown("# 自然言語処理")



cotoha = init_cotoha()


st.markdown("## 入力")
document = st.text_area("分析したい文章を入力してください。")
kw_num = st.number_input("キーワード数の上限",1,100,5)

if st.button("分析"):
    st.markdown("## キーワードハイライト")


    
    parse_result = parse(document, cotoha)
    
    keyword_result = keyword(document, cotoha, max_keyword_num=kw_num)


    
    chunks = parse_result["result"]
    tokens = sum(list(map(lambda x:x["tokens"], chunks)), [])
    
    words = list(map(lambda x:x["form"], tokens))
    
    lemmas = list(map(lambda x:x["lemma"], tokens))
    

    
    keywords = keyword_result["result"]
    kw_forms = list(map(lambda x:x["form"], keywords))
    
    
    
   
    words_kw = [(w,) if w in kw_forms else w for w in words]
   
    
    annotated_text(words_kw)
    