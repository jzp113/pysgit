# -*- coding: utf-8 -*-
import time
from linux.sgitmd import *
from datetime import datetime


class SgitMd(SgitMd):
    def __init__(self, szFlowPath):
        super(SgitMd, self).__init__(szFlowPath)
        self._requestId = 0
        self._userID = ''
        self._password = ''
        self._brokerID = ''
        self._marketDataInstrumentIDs = set()

    def onFrontConnected(self):
        """当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。"""
        reqLoginField = ReqUserLoginField()
        reqLoginField.userID = self._userID
        reqLoginField.password = self._password
        reqLoginField.brokerID = self._brokerID
        self._requestId += 1
        self.reqUserLogin(reqLoginField, self._requestId)

    def onFrontDisconnected(self):
        """0x2003 收到错误报文"""
        print(u'行情服务器连接断开')

    def onRspUserLogin(self, RspUserLoginField, RspInfoField, requestId, final):
        """登录请求响应"""
        # pass
        if RspInfoField.errorID == 0 and self._marketDataInstrumentIDs:
            log = u'行情服务器登陆成功'
            super(SgitMd, self).subscribeMarketData(list(self._marketDataInstrumentIDs))
            self.ready()
        else:
            log = u'行情服务登陆失败，错误码:{0}, 错误信息：{1}'.format(
                RspInfoField.errorID, RspInfoField.errorMsg.decode('gbk'))
        print(log)
        # if self._marketDataInstrumentIDs:
        #     super(SgitMd, self).subscribeMarketData(list(self._marketDataInstrumentIDs))

    def onRspUserLogout(self, UserLogoutField, RspInfoField, requestId, final):
        """登出请求响应"""
        if RspInfoField.errorID == 0:
            log = u'行情服务器登出成功'
        else:
            log = u'行情服务登出失败，错误码:[{0}], 错误信息:[{1}]'.format(
                RspInfoField.errorID, RspInfoField.errorMsg.decode('gbk'))
        print(log)

    def onRspError(self, RspInfoField, requestId, final):
        """错误应答"""
        log = u'行情服务响应错误，错误码:[{0}], 错误信息:[{1}]'.format(
            RspInfoField.errorID, RspInfoField.errorMsg.decode('gbk'))
        print(log)

    def onRtnDepthMarketData(self, DepthMarketDataField):
        """深度行情通知"""
        # for listener in self._barEventListeners:
        # listener.onBarEvent(DepthMarketDataField)
        log = u"{0}, {1}, {2}, {3}".format(
            DepthMarketDataField.instrumentID, DepthMarketDataField.lastPrice, DepthMarketDataField.updateTime,
            str(datetime.now())
        )
        print(log)

    def login(self, szFrontAddress, userID, password, brokerID):
        self._brokerID = brokerID
        self._userID = userID
        self._password = password
        self.registerSpi()
        self.init()
        self.registerFront(szFrontAddress)

    def logout(self):
        userLogoutField = UserLogoutField()
        userLogoutField.userID = self._userID
        userLogoutField.brokerID = self._brokerID
        self._requestId += 1
        self.reqUserLogout(userLogoutField, self._requestId)

    def subscribeMarketData(self, instrumentIDs):
        if instrumentIDs:
            super(SgitMd, self).subscribeMarketData(instrumentIDs)
            self._marketDataInstrumentIDs = self._marketDataInstrumentIDs.union(instrumentIDs)


if __name__ == "__main__":
    ctpMd = SgitMd("./")
    address = "tcp://114.80.207.175:7777"
    ctpMd.login(address, "1703922222", "88", "0212221")

    ctpMd.subscribeMarketData(['Ag(T+D)'])
    ctpMd.join()
