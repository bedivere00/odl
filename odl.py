# -*- coding: utf-8 -*-

import httplib2
import json
import time
import _thread
import tkinter as tk


class OdlUtil:
    __url = ''
    __headers = {'Accept': 'application/json', 'Content-type': 'application/json'}
    __username = "admin"
    __password = "admin"

    def __init__(self, addr):
        self.__url = addr

    def get_load(self, sw, flow_id):
        http = httplib2.Http()
        http.add_credentials(self.__username, self.__password)
        response, content = http.request(
            uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:%d/flow-node'
                '-inventory:table/0/flow/%d ' % (sw, flow_id), method='GET', headers=self.__headers)
        data = json.loads(content)
        port = \
            data["flow-node-inventory:flow"][0]["instructions"]["instruction"][0]["apply-actions"]["action"][0]["output-action"][
                "output-node-connector"]
        return port

    def put_flows(self, sw, flow_id, port_in, port_out):
        http = httplib2.Http()
        http.add_credentials(self.__username, self.__password)
        flows_body = r'{"flow": [{"id": "%d","match":{"in-port": "%d"},"instructions": {"instruction": [{"order": ' \
                     r'"0","apply-actions": {"action": [{"order": "0","output-action": {"output-node-connector": ' \
                     r'"%d"}}]}}]},"priority": "108","cookie": "1","table_id": "0"}]}' % (flow_id, port_in, port_out)
        response, content = http.request(
            uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:%d/flow-node'
                '-inventory:table/0/flow/%d ' % (sw, flow_id),
            body=flows_body, method='PUT', headers=self.__headers)


def dynamic(odl):
    while True:
        odl.put_flows(1, 11, 1, 4)
        odl.put_flows(5, 54, 1, 4)
        time.sleep(30)
        odl.put_flows(1, 11, 1, 5)
        odl.put_flows(5, 54, 2, 4)
        time.sleep(30)
        odl.put_flows(1, 11, 1, 6)
        odl.put_flows(5, 54, 3, 4)
        time.sleep(30)


odla = OdlUtil('http://127.0.0.1:8181')
odla.put_flows(2, 25, 1, 2)
odla.put_flows(3, 35, 1, 2)
odla.put_flows(4, 45, 1, 2)
try:
    _thread.start_new_thread(dynamic, (odla,))
except:
    print("Error: unable to start thread")

root = tk.Tk()
# 进入消息循环
root.title("路径验证")
root.geometry('500x180')

tk.Label(root, text="验证", font=("Arial", 18), width=5, height=2).pack()

frm = tk.Frame(root, pady=10)
#left
frm_L = tk.Frame(frm)
frm_LT = tk.Frame(frm_L)
tk.Label(frm_LT, text='    源地址：', font=('Arial', 12)).pack(side=tk.LEFT)
sip = tk.StringVar()
tk.Entry(frm_LT, textvariable=sip).pack(side=tk.RIGHT)
frm_LT.pack(side=tk.TOP)

frm_LB = tk.Frame(frm_L)
tk.Label(frm_LB, text='目的地址：', font=('Arial', 12)).pack(side=tk.LEFT)
dip = tk.StringVar()
tk.Entry(frm_LB, textvariable=dip).pack(side=tk.RIGHT)
frm_LB.pack(side=tk.TOP)
frm_L.pack(side=tk.LEFT)

#right
frm_R = tk.Frame(frm, padx=10)
tk.Label(frm_R, text="传输路径：", font=("Arial", 13)).pack(side=tk.TOP)
path = tk.StringVar()
tk.Entry(frm_R, textvariable=path, ).pack(side=tk.TOP)


def printroot():
    if sip.get() == "10.0.0.1" and dip.get() == "10.0.0.4":
        port = odla.get_load(1, 11)
        root = {"4": "S1-S2-S5", "5": "S1-S3-S5", "6": "S1-S4-S5"}.get(port, "error")
        path.set(root)
    else:
        path.set("找不到信息")

frm_R.pack(side=tk.LEFT)
frm.pack(side=tk.TOP)
tk.Button(root, text="查询", font=("Arial", 16), command=printroot).pack(side=tk.TOP)
root.mainloop()

