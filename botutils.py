

#  utility file for messenger bot

import requests
import json
from credentials import credentials



token = credentials['ACCESS_TOKEN']


def get_started_btn():
    params = {
        "access_token":token,
    }
    payload = json.dumps({
            "get_started":{
                        "payload":"@get_started"
            }
    })

    resp = requests.post(
                    "https://graph.facebook.com/v2.6/me/messenger_profile",
                    params=params,
                    data=payload,
                    headers={
                        'Content-type': 'application/json'
                    }
    )
    return resp.json()

class json_response_builder():

    def __init__(self):
        pass

    def quick_replies_from_list(self,qk_list):
        ''' builds up quick reply response object using the suppied list.

            content-type options : text or location

            input: ([title,payload,content-type])

        '''
        quick_replies = []
        for i in range(0,len(qk_list)):
            if len(qk_list[i]) < 3:
                print("Not enough parameters in list {}!".format(i))
            else:
                if qk_list[i][2] == "location":
                    quick_replies.append({
                        "content_type":qk_list[i][2],
                    })
                else:
                    quick_replies.append({
                        "content_type":qk_list[i][2],
                        "title":qk_list[i][0],
                        "payload":qk_list[i][1],
                    })
        return quick_replies

    def build_generic_elements(self,elements):
        """ arg format :({
                            "element_data":[{"data":[title,img_url,sub_title,action_url],
                                            "button":[
                                                {"data":[type,url,title]}]
                                            },]
                        })

            If you don't understand this function don't fret. It's fucking nuts. It takes a while to
            understand. I'll explicity add comments in it so you can understand it better.
            This function still needs to be updated.

            This function builds the template based on the given data.
            The data is structured accordingly, then this function accesses it.
            Multiple template data can be passed in the struct, that's why the for loop.
            Button data doesnt support multiple buttons for a single card. Just one button for now.


        """
        element_list = []
        len_element = len(elements['element_data'])

        # constructs the generic elements payload
        # loops through the multiple template data struct
        for x in range(len_element):
            # This condition allows us to add a different type to the cards
            # Initially this function only supported web_url type that
            # lets you open a browser instace inside the bot.
            # Now I've added the postback type. This type responds like the quick
            # reply button.
            if elements['element_data'][x]['button'][0] == "postback":
                button_data = {
                    "type":"postback",
                    "payload":elements['element_data'][x]['button'][1],
                    "title":"{}".format(elements['element_data'][x]['button'][2]),
                }
            elif elements['element_data'][x]['button'][0] == "web_url":
                # default type for the card
                button_data = {
                    "type":"web_url",
                    "url":elements['element_data'][x]['button'][1],
                    "title":"{}".format(elements['element_data'][x]['button'][2]),
                }

            element_list.append({
                "title":elements['element_data'][x]['data'][0],
                "image_url":elements['element_data'][x]['data'][1],
                "subtitle":elements['element_data'][x]['data'][2],
                "default_action":{
                    "type": "web_url",
                    "url": elements['element_data'][x]['data'][3],
                    "webview_height_ratio": "full",
                },
                "buttons":[button_data] # button data dict is inserted into the list
            })
        return element_list



class Messenger_wrapper(object):

    def __init__(self,token):
        self.params = { "access_token": token }
        self.headers = { 'Content-type': 'application/json' }
        self.graph_api_endpoint = "https://graph.facebook.com/v2.6/me/messages"
        # create a response builder object for later use
        self.x = json_response_builder()

    def send(self,user_id,payload):
        #payload = payload
        payload["recipient"] = {"id":str(user_id)}
        self.resp = requests.post(self.graph_api_endpoint,params=self.params,data=json.dumps(payload),headers=self.headers)
        return self.resp.json()

    def get_started_btn(self):
        payload = {}
        payload["get_started"] = {"payload":"@get_started"}
        r = self.send("None",payload)
        return r

    def send_text_message(self,user_id,user_msg):
        payload = {"message":{"text":user_msg}}
        r = self.send(user_id,payload=payload)
        return r

    def quick_reply(self,user_id,text,qk_payload):

        qk_resp = self.x.quick_replies_from_list(qk_payload)
        payload = {
            "message":{
                "text":text,
                "quick_replies":qk_resp,
            }
        }
        r = self.send(user_id,payload=payload)
        return r

    def generic_template(self,user_id,element_payload):
        #  f = {"element_data":[{"data":["Test","https://www.target.com.au/medias/static_content/product/images/large/34/01/A873401.jpg","sub_title","https://www.target.com.au/p/essentials-t-shirt-light-grey/58106341"],"button":["https://www.target.com.au/p/essentials-t-shirt-light-grey/58106341","Title"]},]}
        # builds the payload for elements in JSON format
        elements = self.x.build_generic_elements(element_payload)
        payload={
          "message":{
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"generic",
                "elements": elements,
              }
            }
          }
        }
        r = self.send(user_id,payload=payload)
        return r

def Persistant_menu(show_menu=True,composer_input=True):
    params = {
        "access_token":token,
    }
    payload = json.dumps({
        "persistent_menu":[
        {
          "locale":"default",
          "composer_input_disabled":True,
          "call_to_actions":[
            {
              "title":"🕕 Top 5 coins last 24hr",
              "type":"postback",
              "payload":"@show_top_coins"
            },
            {
              "title":"🎁 Get Premium for $4.99 🎉",
              "type":"postback",
              "payload":"@show_premium"
            },
            {
                "title":"🗄 Menu",
                "type":"nested",
                "call_to_actions":[
                      {
                        "title":"Premium features",
                        "type":"postback",
                        "payload":"@show_premium_features🤘"
                      },
                      {
                         "title":"✉️ Subscriptions",
                         "type":"nested",
                         "call_to_actions":[

                             {
                               "title":"💝 Subscribe",
                               "type":"postback",
                               "payload":"@subscribe"
                             },
                             {
                               "title":"💔 Unsubscribe",
                               "type":"postback",
                               "payload":"@unsubscribe"
                             }
                         ]
                       },
                  ]

            }
          ]
        },
        {
          "locale":"zh_CN",
          "composer_input_disabled":False,
        }
       ]
    })
    resp = requests.post(
        "https://graph.facebook.com/v2.6/me/messenger_profile",
        params=params,
        data=payload,
        headers={
            'Content-type': 'application/json'
        }
    )
    return resp.json()
