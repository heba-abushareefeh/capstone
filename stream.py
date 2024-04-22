import streamlit  as st
import numpy as np
import pandas as pd
from capstone import *
from streamlit_option_menu import option_menu
import plotly.figure_factory as ff
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

class Home:   
 def get_data(self):
    return st.session_state["dataset"]
    

 def get_info(self,df):
      st.write("## Numeric data info")
      info = get_info(df)
      st.session_state["info"]=info
      st.write(info[0])
      st.markdown("---")
      st.write("## non_Numeric data info")
      st.write(info[1])
      
      
 def preprocessing_data(self):
     st.session_state["dataset2"] = clean_data(st.session_state["dataset"])
     return st.session_state["dataset2"]
 
 def get_encoding(self):
     st.session_state["dataset2"]=encoding_data(
        st.session_state["dataset2"],
        st.session_state["features"]  ,
        is_ordinal,
        )
     return  st.session_state["dataset2"]
 def get_scalling(self):
      scaler(st.session_state["dataset2"],st.session_state["scalling"])
      return st.session_state["dataset2"]
  
 def splitting(self):
     splitting=split(st.session_state["dataset2"][st.session_state["features"]],st.session_state["dataset2"][y_class],step_size)
     return splitting
     
     
#variable and object
#-----------------------------------------

h=Home()
if "step_number" not in st.session_state:
    st.session_state["step_number"] = 1

    
if "splitting" not in st.session_state:
    st.session_state["splitting"] = {}
    
#------------------------------------------   
#button
def previous():
   st.session_state["step_number"] -=1

def next():
    st.session_state["step_number"] +=1
    

#-------------------------------------------

#minue
with st.sidebar:
 select = option_menu("☰", ["Home", "visualization"], 
        icons=['house'], menu_icon="☰", default_index=0)
#---------------------------------------------

    
path=None  
if select=="Home" :
    
 # data uploading---------------------------------------------------------------------------------
 
 if st.session_state["step_number"] == 1:  
    # st.session_state.clear()
    # st.session_state["step_number"] = 1
    
    st.write("# Load Your Dataset")
    path = st.file_uploader(
        "dataset_uploading",
        label_visibility="hidden",
        type="csv",
    )
    if path is not None:
        st.session_state["step_number"] += 1
        st.session_state["dataset"] =get_data(path)
        st.write(st.session_state["dataset"])
        st.rerun()
    
    
    
 # prepareing the data step by step--------------------------------------------------------------
 
 if st.session_state["step_number"] == 2:
    
   selected= option_menu(None, ["DataSet", "Information", "Preprocessing","Encoding","Scalling","splitting","train_model"], 
   
    # icons=['house', 'ⓘ', "📊", 'card-list' ,'cloud-upload'], 
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "15px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "gray"}
        }
    )
   
   


   
   if selected=="DataSet":
    
    st.button("Previous", on_click=previous)
    st.write(h.get_data())

   if selected=="Information":
       h.get_info(st.session_state["dataset"])
       
   if selected =="Preprocessing":
      df2=h.preprocessing_data()
      st.write(df2 )
      st.write("#### info after preprocessing:")
      st.write(h.get_info(df2))
      
      
   if selected=="Encoding":
        str_col= list(st.session_state["dataset2"].select_dtypes(include=object))
        is_ordinal =[]
        i=0
        
        #select columns need encoding (must be non numeric)
        st.session_state["features"] = st.multiselect(
        label="select features",
        options=str_col)
        
        #ordunal or not?
        for feature in st.session_state["features"]:
          label = f"Is {feature} Ordinal?"
          is_ordinal.append (st.radio(label, options=[True, False]))
          i+=1
        
         #encoding button
        encoding_button=st.button("encoding")
        if encoding_button:
         
         
         st.write("## Data after encoding")
         st.write(h.get_encoding())
        
   if selected=="Scalling":
        int_col= list(st.session_state["dataset2"].select_dtypes(np.number))
        
        st.session_state["scalling"] = st.multiselect(
        label="select features to scale",
        options=int_col)
        
        
        scalling_button=st.button("scalling")
       
        if scalling_button:
         scaler(
         st.session_state["dataset2"],st.session_state["scalling"])
         st.write(st.session_state["dataset2"])
   if selected=="splitting":
      
        col = st.columns(2)
        #select x
        st.session_state["features"] = col[0].multiselect(
        label="select features",
        options=st.session_state["dataset2"].columns)
        
        #select y
        y_class=col[1].multiselect(
        label="select class",
        options=st.session_state["dataset2"].columns.drop(st.session_state["features"]),
        max_selections=1,
        # default=st.session_state["label"],
        on_change=st.write("change"),
        )
        
        step_size=st.number_input("Test Size in float😁", min_value=0.1, max_value=1.0, value=0.3, step=0.1)
        splitting_button=st.button("splitting")
       
        if splitting_button:
        #  splitting=split(st.session_state["dataset"][st.session_state["features"]],st.session_state["dataset"][y_class],step_size)
        
         splitting=h.splitting()
         st.session_state["splitting"]=splitting
         st.write("## train set")
         st.write("size:",len(splitting[0]))
         st.write(splitting[0])
         st.write("## test set")
         st.write("size:",len(splitting[1]))
         st.write(splitting[1])
         
    
   if selected == "train_model":
     if st.session_state["splitting"] == {}:
          st.write("do spliting first and encoding first🔁")
       
     else:
           is_continous=[]
           label = f"Is y (class) Continous?"
           is_continous.append (st.radio(label, options=[True, False]))
           model_button=st.button("model")
           if model_button:
            pred=model_train(st.session_state["splitting"][0],st.session_state["splitting"][1],is_continous[0])
            # st.write(pred)
    

if select=="visualization":
    #  st.session_state["step_number"] = 1
    
     if "plot_name" not in st.session_state:
         st.session_state["plot_name"] = None
         
     st.write("### select plot ")
     col1, col2,col3,col4 = st.columns([9,8,7,6])
     plot_button=col1.button("plot")
     hist_button=col2.button("histogram")
     corr_button=col3.button("corellation")
     plotly_button=col4.button("hist and distributed")
     show_button=col1.button("show")
     
     if plot_button:
         st.session_state["plot_name"] = "plot"
         
         
     elif hist_button:
         st.session_state["plot_name"] = "hist"
     
     elif corr_button:
         st.session_state["plot_name"] = "corellation"
    
     elif plotly_button:
         st.session_state["plot_name"] = "hist and distributed"
         
    
         
        
     try:   
        st.session_state["dataset2"]=h.preprocessing_data()
     except:
       st.markdown('<span style="color:red">:x:  download data  </span>', unsafe_allow_html=True)
     
     if st.session_state["plot_name"] == "plot":
          st.write("Plot Page")
          
        
          x_axis=st.multiselect(
        label="select x_axis",
        options=st.session_state["dataset2"].columns,
        max_selections=1,
        
        )
          y_axis=st.multiselect(
        label="select y_axis",
        options=st.session_state["dataset2"].columns,
        max_selections=1,
        
        )
          
          if show_button :
            if x_axis and y_axis :
             fig = px.line(st.session_state["dataset2"], x=x_axis[0], y=y_axis[0], title='Line Plot')
             st.plotly_chart(fig)
            else:
              st.write("select feauture first")
         
     elif st.session_state["plot_name"] =="hist":
      column = st.selectbox(
        label="Select column for histogram",
        options=st.session_state["dataset2"].columns
    )
      if show_button:
       if column:
        fig = px.histogram(st.session_state["dataset2"], x=column, marginal="rug",
                   hover_data=st.session_state["dataset2"].columns)
        st.write(fig)
       else:
        st.write("Please select a column for the histogram.")
        
     elif st.session_state["plot_name"] =="corellation":
        if show_button:
         corr_matrix = st.session_state["dataset2"].select_dtypes(np.number).corr()
         st.write("corr figure ")
         fig, ax = plt.subplots()
         sns.heatmap(corr_matrix, ax=ax)
         st.write(fig)
         
     elif st.session_state["plot_name"] =="hist and distributed":
         
         feature= st.selectbox(
        label="Select column for histogram",
        options=st.session_state["dataset2"].columns)
         
         group_labels = st.selectbox(
        label="Select group_labels",
        options=st.session_state["dataset2"].columns)
         if show_button:
            if   feature and  group_labels:
             fig = px.histogram(st.session_state["dataset2"], x=feature, marginal="rug",color=group_labels,
                   hover_data=st.session_state["dataset2"].columns)
             st.write(fig)
            else:
                st.write("Please select a featuure and group_label for the histogram.")
                
                
# if select =='Save Project':
#   group_labels = st.selectbox(
#         label="after",
#         options=["preprocessing","scalling","encoding",])
        