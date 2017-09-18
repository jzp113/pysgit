# -*- coding: utf-8 -*-
from datetime import datetime
from linux.sgitmd import *
from sgitconf import deploy

class SgitMd(SgitMd):
    def __init__(self, szFlowPath, usingUdp=False, multicast=False):
        super(SgitMd, self).__init__(szFlowPath, usingUdp, multicast)
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

    def onFrontDisconnected(self, reasonCode):
        """0x2003 收到错误报文"""
        print(u'行情服务器连接断开，错误码是%d', reasonCode)

    def onHeartBeatWarning(self, lapsedTime):
        """@:param lapsedTime 距离上次接收报文的时间"""
        pass

    def onRspUserLogin(self, RspUserLoginField, RspInfoField, requestId, final):
        """登录请求响应"""
        # pass
        if RspInfoField.errorID == 0:
            log = u'行情服务器登陆成功'
        else:
            log = u'行情服务登陆失败，错误码:{0}, 错误信息：{1}'.format(
                RspInfoField.errorID, RspInfoField.errorMsg.decode('gbk'))
        print "maxorderref" + RspUserLoginField.maxOrderRef
        print(log)
        if self._marketDataInstrumentIDs:
            self.subscribeMarketData(list(self._marketDataInstrumentIDs))

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

    def onRspSubMarketData(self, SpecificInstrumentField, RspInfoField, requestId, final):
        """订阅行情应答"""
        print(u'订阅的instrumentID：{0}，响应结果，错误码：[{1}]，错误信息：【{2}]'.format(
            SpecificInstrumentField.instrumentID, RspInfoField.errorID, RspInfoField.errorMsg.decode('gbk')))

    def onRspUnSubMarketData(self, SpecificInstrumentField, RspInfoField, requestId, final):
        """取消订阅行情应答"""
        pass

    def onRspSubForQuoteRsp(self, SpecificInstrumentField, RspInfoField, requestId, final):
        """订阅询价应答"""
        pass

    def onRspUnSubForQuoteRsp(self, SpecificInstrumentField, RspInfoField, requestId, final):
        """取消订阅询价应答"""
        pass

    def onRtnDepthMarketData(self, DepthMarketDataField):
        """深度行情通知"""
        log = u"{0}, {1}, {2}, {3}".format(
            DepthMarketDataField.instrumentID, DepthMarketDataField.lastPrice, DepthMarketDataField.updateTime,
            str(datetime.now())
        )
        print(log)

    def onRtnForQuoteRsp(self, ForQuoteRspField):
        """询价通知"""
        pass

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

    def unSubscribeMarketData(self, instrumentIDs):
        if instrumentIDs:
            super(SgitMd, self).unSubscribeMarketData(instrumentIDs)
            self._marketDataInstrumentIDs = self._marketDataInstrumentIDs.difference(instrumentIDs)


if __name__ == "__main__":
    sgitMd = SgitMd("./")
    # print(sgitMd.getApiVersion())

    sgitMd.login(*deploy['MD'])
    sgitMd.subscribeMarketData(['Ag(T+D)'])
    sgitMd.join()
