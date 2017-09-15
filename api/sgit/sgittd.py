# -*- coding: utf-8 -*-

from linux.sgittd import *
from sgitconf import deploy

class SgitTd(SgitTd):
    def __init__(self, szFlowPath):
        super(SgitTd, self).__init__(szFlowPath)
        self._requestId = 0
        self._userID = ''
        self._password = ''
        self._brokerID = ''

        self._errorCode = 0
        self._orderRef = 0
        self.frontID = None  # 前置编号
        self.sessionID = None  # 会话编号
        # self._barEventListeners = set()
        self.__rspQryOrder_dic = {}  # 委托单暂存
        self.__rspQryInvestorPositionDetaild_dic = {}  # 持仓明细暂存

    def logAttr(self, clas, name):
        attrs = [attr for attr in dir(clas)
                 if not attr.startswith('__')]
        values = [(attr, getattr(clas, attr)) for attr in attrs]
        print u"{}: {}".format(name, str(values))


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
        pass

    def onRspUserLogin(self, RspUserLoginField, RspInfoField, requestId, final):
        """登录请求响应"""
        print("sessionID:{}".format(RspUserLoginField.sessionID))
        if RspInfoField.errorID == 0:
            self.frontID = RspUserLoginField.frontID
            self.sessionID = RspUserLoginField.sessionID
            print("orderRef: {}".format(RspUserLoginField.maxOrderRef))
            if RspUserLoginField.maxOrderRef:
                self._orderRef = RspUserLoginField.maxOrderRef
            log = u'交易服务器登陆成功'
            # settlementInfoConfirmField = SettlementInfoConfirmField()
            # settlementInfoConfirmField.brokerID = self._brokerID
            # settlementInfoConfirmField.investorID = self._userID
            # self._requestId += 1
            # self.reqSettlementInfoConfirm(settlementInfoConfirmField, self._requestId)
            # self.qryPosition()
        else:
            log = u'交易服务登陆失败，错误码:{0}, 错误信息：{1}'.format(
                RspInfoField.errorID, RspInfoField.errorMsg.decode('gbk'))
        print(log)

    def onRspUserLogout(self, UserLogoutField, RspInfoField, requestId, final):
        """登出请求响应"""
        if RspInfoField.errorID == 0:
            log = u'交易服务器登出成功'
        else:
            log = u'交易服务登出失败，错误码:[{0}], 错误信息:[{1}]'.format(
                RspInfoField.errorID, RspInfoField.errorMsg.decode('gbk'))
        print(log)

    def onRspOrderInsert(self, InputOrderField, RspInfoField, requestId, final):
        """报单录入请求响应"""
        print(u"onRspOrderInsert --- brokerID:{0}, orderRef:{1}, price:{2}, volume:{3}, orderPriceType:{4},"
              u"direction: {5}, combOffsetFlag: {6}, combHedgeFlag:{7}, contingentCondition: {8}, forceCloseReason:{9},"
              u"isAutoSuspend: {10}, timeCondition: {11}, volumeCondition:{12}, minVolume: {13}, instrumentID: {14}"
              .format(InputOrderField.brokerID, InputOrderField.orderRef, InputOrderField.limitPrice,
                      InputOrderField.volumeTotalOriginal, InputOrderField.orderPriceType, InputOrderField.direction,
                      InputOrderField.combOffsetFlag, InputOrderField.combHedgeFlag,
                      InputOrderField.contingentCondition,
                      InputOrderField.forceCloseReason, InputOrderField.isAutoSuspend, InputOrderField.timeCondition,
                      InputOrderField.volumeCondition, InputOrderField.minVolume, InputOrderField.instrumentID))
        print(u"onRspOrderInsert --- errorCode:{0}, errorMsg:{1}.".format(
            RspInfoField.errorID, RspInfoField.errorMsg.decode('gbk')))

    def onRspOrderAction(self, InputOrderActionField, RspInfoField, requestId, final):
        """报单操作请求响应"""
        print u"onRspOrderAction --- sessionId: {0}, frontID: {1}, orderRef: {2}".format(
            InputOrderActionField.sessionID,
            InputOrderActionField.frontID, InputOrderActionField.orderRef)
        print(u"onRspOrderAction --- errorCode:{0}, errorMsg:{1}.".format(
            RspInfoField.errorID, RspInfoField.errorMsg.decode('gbk')))

    def onRspSettlementInfoConfirm(self, SettlementInfoConfirmField, RspInfoField, requestId, final):
        """投资者结算结果确认响应"""
        print(
            u"onRspSettlementInfoConfirm --- brokerID:{0}, investorID:{1}，confirmDate:{2}，confirmTime:{3}.".format(
                SettlementInfoConfirmField.brokerID, SettlementInfoConfirmField.investorID,
                SettlementInfoConfirmField.confirmDate, SettlementInfoConfirmField.confirmTime))
        print(u"onRspSettlementInfoConfirm --- errorCode:{0}，errorMsg:{1}.".format(
            RspInfoField.errorID, RspInfoField.errorMsg.decode('gbk')))

    def onRspQryOrder(self, OrderField, RspInfoField, requestId, final):
        """请求查询报单响应"""
        if OrderField:  # 这个字段也可能为空
            print(
                u"onRspQryOrder --- brokerID:{0}, orderRef:{1}, limitPrice:{2}, volume:{3}, orderPriceType:{4},"
                u"direction: {5}, combOffsetFlag: {6},combHedgeFlag:{7},contingentCondition: {8},forceCloseReason: {9},"
                u"isAutoSuspend: {10}, timeCondition: {11}, volumeCondition:{12}, minVolume: {13}, instrumentID: {14}"
                    .format(OrderField.brokerID, OrderField.orderRef, OrderField.limitPrice,
                            OrderField.volumeTotalOriginal,
                            OrderField.orderPriceType, OrderField.direction, OrderField.combOffsetFlag,
                            OrderField.combHedgeFlag,
                            OrderField.contingentCondition, OrderField.forceCloseReason, OrderField.isAutoSuspend,
                            OrderField.timeCondition,
                            OrderField.volumeCondition, OrderField.minVolume, OrderField.instrumentID))
            self.__rspQryOrder_dic[OrderField.orderRef] = OrderField

        if RspInfoField:  # 这个字段竟然能能返回为空
            print(u"onRspQryOrder --- errorCode: {0}, errorMsg:{1}.".format(
                RspInfoField.errorID, RspInfoField.errorMsg.decode("gbk")))

    def onRspQryTrade(self, TradeField, RspInfoField, requestId, final):
        """请求查询成交响应"""
        pass

    def onRspQryInvestorPosition(self, InvestorPositionField, RspInfoField, requestId, final):
        """请求查询投资者持仓响应"""
        # print(u"onRspQryInvestorPosition -- instrumentID:{0}, brokerID:{1}, investorID:{2}, posiDirection:{3},"
        #       u"positionDate: {4}, position: {5}".format(InvestorPositionField.instrumentID,
        #                                                  InvestorPositionField.brokerID,
        #                                                  InvestorPositionField.investorID,
        #                                                  InvestorPositionField.posiDirection,
        #                                                  InvestorPositionField.positionDate,
        #                                                  InvestorPositionField.position))
        self.logAttr(InvestorPositionField, u"投资者持仓")
        if RspInfoField:  # 这个字段竟然能能返回为空
            print(u"onRspQryInvestorPosition -- errorCode: {0}, errorMsg:{1}.".format(
                RspInfoField.errorID, RspInfoField.errorMsg.decode("gbk")))

    def onRspQryTradingAccount(self, TradingAccountField, RspInfoField, requestId, final):
        """请求查询资金账户响应"""
        attrs = [attr for attr in dir(TradingAccountField)
                 if not attr.startswith('__')]
        values = [(attr, getattr(TradingAccountField, attr)) for attr in attrs]
        print u"账号详情: %s" % str(values)

    def onRtnTrade(self, TradeField):
        # """成交通知"""
        attrs = [attr for attr in dir(TradeField)
                 if not attr.startswith('__')]
        values = [(attr, getattr(TradeField, attr)) for attr in attrs]
        print u"成交通知: %s" % str(values)

    def login(self, szFrontAddress, userID, password, brokerID):
        self.__address = szFrontAddress
        self._userID = userID
        self._password = password
        self._brokerID = brokerID
        self.registerSpi()
        # 数据重传模式设为从本日开始
        # tert.restart, tert.resume, tert.quick
        self.subscribePrivateTopic(tert.resume)
        self.subscribePublicTopic(tert.resume)
        self.init()
        self.registerFront(szFrontAddress)

    def logout(self):
        userLogoutField = UserLogoutField()
        userLogoutField.userID = self._userID
        userLogoutField.brokerID = self._brokerID
        self._requestId += 1
        self.reqUserLogout(userLogoutField, self._requestId)

    # ----------------------------------------------------------------------
    def qryPosition(self):
        """查询持仓"""
        qryInvestorPositionField = QryInvestorPositionField()
        qryInvestorPositionField.brokerID = self._brokerID
        qryInvestorPositionField.investorID = self._userID
        # qryInvestorPositionField.instrumentID = "Ag(T+D)"
        self._requestId += 1
        self.reqQryInvestorPosition(qryInvestorPositionField, self._requestId)
        return self._requestId

    def onRspQryInvestorPositionDetail(self, InvestorPositionDetailField, RspInfoField, requestId, final):
        """请求查询投资者持仓明细响应"""
        # print(u"onRspQryInvestorPositionDetail -- instrumentID:{0}, brokerID:{1}, investorID:{2}, Direction:{3},"
        #       u"tradingDay: {4}, tradeID: {5},openPrice:{6},volume:{7}".format(
        #     InvestorPositionDetailField.instrumentID,
        #     InvestorPositionDetailField.brokerID,
        #     InvestorPositionDetailField.investorID,
        #     InvestorPositionDetailField.direction,
        #     InvestorPositionDetailField.tradingDay,
        #     InvestorPositionDetailField.positionProfitByTrade,
        #     InvestorPositionDetailField.openPrice,
        #     InvestorPositionDetailField.volume,
        # )
        # )
        # self.logAttr(InvestorPositionDetailField, u"持仓明细")
        # self.__rspQryInvestorPositionDetaild_dic[InvestorPositionDetailField.tradeID] = InvestorPositionDetailField
        if RspInfoField:  # 这个字段竟然能能返回为空
            print(u"onRspQryInvestorPositionDetail -- errorCode: {0}, errorMsg:{1}.".format(
                RspInfoField.errorID, RspInfoField.errorMsg.decode("gbk")))

    # ----------------------------------------------------------------------
    def qryPositionDetail(self):
        """查询持仓详情"""
        qryInvestorPositionDetailField = QryInvestorPositionDetailField()
        qryInvestorPositionDetailField.brokerID = self._brokerID
        qryInvestorPositionDetailField.investorID = self._userID
        # qryInvestorPositionDetailField.instrumentID = ""
        self._requestId += 1
        self.reqQryInvestorPositionDetail(qryInvestorPositionDetailField, self._requestId)
        return self._requestId

    def qryTradingAccount(self):
        """查询用户资金"""
        qryTradingAccountField = QryTradingAccountField()
        qryTradingAccountField.brokerID = self._brokerID
        qryTradingAccountField.investorID = self._userID
        self._requestId += 1
        self.reqQryTradingAccount(qryTradingAccountField, self._requestId)

    def reqQryOrder(self):
        """查询委托"""
        qryOrderField = QryOrderField()
        qryOrderField.brokerID = self._brokerID
        qryOrderField.investorID = self._userID
        # qryOrderField.instrumentID = ""
        self._requestId += 1
        super(SgitTd, self).reqQryOrder(qryOrderField, self._requestId)
        return self._requestId

    # ----------------------------------------------------------------------
    def sendOrder(self, instrumentID, direction, orderPriceType, offsetFlag, price, volume):
        """发单
        :param symbol: 合约号
        :param direction: 买卖方向
            - 买 THOST_FTDC_D_Buy '0'
            - 卖 THOST_FTDC_D_Sell '1'
        :param orderPriceType: 报单价格条件   #只支持限价，部分支持市价
            - 任意价 THOST_FTDC_OPT_AnyPrice '1'
            - 限价 THOST_FTDC_OPT_LimitPrice '2'
            - 最优价 THOST_FTDC_OPT_BestPrice '3'
            - 最新价 THOST_FTDC_OPT_LastPrice '4'
            - 最新价浮动上浮1个ticks THOST_FTDC_OPT_LastPricePlusOneTicks '5'
            - 最新价浮动上浮2个ticks THOST_FTDC_OPT_LastPricePlusTwoTicks '6'
            - 最新价浮动上浮3个ticks THOST_FTDC_OPT_LastPricePlusThreeTicks '7'
            - 卖一价 THOST_FTDC_OPT_AskPrice1 '8'
            - 卖一价浮动上浮1个ticks THOST_FTDC_OPT_AskPrice1PlusOneTicks '9'
            - 卖一价浮动上浮2个ticks THOST_FTDC_OPT_AskPrice1PlusTwoTicks 'A'
            - 卖一价浮动上浮3个ticks THOST_FTDC_OPT_AskPrice1PlusThreeTicks 'B'
            - 买一价 THOST_FTDC_OPT_BidPrice1 'C'
            - 买一价浮动上浮1个ticks THOST_FTDC_OPT_BidPrice1PlusOneTicks 'D'
            - 买一价浮动上浮2个ticks THOST_FTDC_OPT_BidPrice1PlusTwoTicks 'E'
            - 买一价浮动上浮3个ticks THOST_FTDC_OPT_BidPrice1PlusThreeTicks 'F'
            - 五档价 THOST_FTDC_OPT_FiveLevelPrice 'G'
        :param offsetFlag: 组合开平标志
            - 开仓 THOST_FTDC_OF_Open '0'
            - 平仓 THOST_FTDC_OF_Close '1'
            - 强平 THOST_FTDC_OF_ForceClose '2'
            - 平今 THOST_FTDC_OF_CloseToday '3'
            - 平昨 THOST_FTDC_OF_CloseYesterday '4'
            - 强减 THOST_FTDC_OF_ForceOff '5'
            - 本地强平 THOST_FTDC_OF_LocalForceClose '6'
        :param price: 价格
        :param volume: 数量

        :enum combHedgeFlag: 组合投机套保标志
            - 投机: THOST_FTDC_HF_Speculation '1'
            - 套利：THOST_FTDC_HF_Arbitrage '2'
            - 套保：THOST_FTDC_HF_Hedge '3'
            - 做市商：THOST_FTDC_HF_MarketMaker '5'

        :enum contingentCondition: 触发条件
            - 立即 THOST_FTDC_CC_Immediately '1'
            - 止损 THOST_FTDC_CC_Touch '2'
            - 止赢 THOST_FTDC_CC_TouchProfit '3'
            - 预埋单 THOST_FTDC_CC_ParkedOrder '4'
            - 最新价大于条件价 THOST_FTDC_CC_LastPriceGreaterThanStopPrice '5'
            - 最新价大于等于条件价 THOST_FTDC_CC_LastPriceGreaterEqualStopPrice '6'
            - 最新价小于条件价 THOST_FTDC_CC_LastPriceLesserThanStopPrice '7'
            - 最新价小于等于条件价 THOST_FTDC_CC_LastPriceLesserEqualStopPrice '8'
            - 卖一价大于条件价 THOST_FTDC_CC_AskPriceGreaterThanStopPrice '9'
            - 卖一价大于等于条件价 THOST_FTDC_CC_AskPriceGreaterEqualStopPrice 'A'
            - 卖一价小于条件价 THOST_FTDC_CC_AskPriceLesserThanStopPrice 'B'
            - 卖一价小于等于条件价 THOST_FTDC_CC_AskPriceLesserEqualStopPrice 'C'
            - 买一价大于条件价 THOST_FTDC_CC_BidPriceGreaterThanStopPrice 'D'
            - 买一价大于等于条件价 THOST_FTDC_CC_BidPriceGreaterEqualStopPrice 'E'
            - 买一价小于条件价 THOST_FTDC_CC_BidPriceLesserThanStopPrice 'F'
            - 买一价小于等于条件价 THOST_FTDC_CC_BidPriceLesserEqualStopPrice 'H'
        :enum forceCloseReason: 强平原因
            - 非强平 THOST_FTDC_FCC_NotForceClose '0'
            - 资金不足 THOST_FTDC_FCC_LackDeposit '1'
            - 客户超仓 THOST_FTDC_FCC_ClientOverPositionLimit '2'
            - 会员超仓 THOST_FTDC_FCC_MemberOverPositionLimit '3'
            - 持仓非整数倍 THOST_FTDC_FCC_NotMultiple '4'
            - 违规 THOST_FTDC_FCC_Violation '5'
            - 其它 THOST_FTDC_FCC_Other '6'
            - 自然人临近交割 THOST_FTDC_FCC_PersonDeliv '7'
        :enum timeCondition: 有效期类型
            - 立即完成，否则撤销 THOST_FTDC_TC_IOC '1'
            - 本节有效 THOST_FTDC_TC_GFS '2'
            - 当日有效 THOST_FTDC_TC_GFD '3'
            - 指定日期前有效 THOST_FTDC_TC_GTD '4'
            - 撤销前有效 THOST_FTDC_TC_GTC '5'
            - 集合竞价有效 THOST_FTDC_TC_GFA '6'
        :enum volumeCondition: 成交量类型
            - 任何数量 THOST_FTDC_VC_AV '1'
            - 最小数量 THOST_FTDC_VC_MV '2'
            - 全部数量 THOST_FTDC_VC_CV '3'
        """
        self._orderRef += 1

        inputOrderField = InputOrderField()
        inputOrderField.brokerID = self._brokerID
        inputOrderField.investorID = self._userID
        inputOrderField.userID = self._userID
        inputOrderField.orderRef = str(self._orderRef)

        inputOrderField.instrumentID = instrumentID
        inputOrderField.limitPrice = price
        inputOrderField.volumeTotalOriginal = volume

        inputOrderField.orderPriceType = orderPriceType
        inputOrderField.direction = direction
        inputOrderField.combOffsetFlag = offsetFlag

        inputOrderField.combHedgeFlag = '1'  # 投机单
        inputOrderField.contingentCondition = '1'  # 立即发单
        inputOrderField.forceCloseReason = '0'  # 非强平
        inputOrderField.isAutoSuspend = 0  # 非自动挂起
        inputOrderField.timeCondition = '3'  # 今日有效
        inputOrderField.volumeCondition = '1'  # 任意成交量
        inputOrderField.minVolume = 1  # 最小成交量为1
        # inputOrderField.GTDDate = ""
        # inputOrderField.stopPrice = 0

        self._requestId += 1
        self.reqOrderInsert(inputOrderField, self._requestId)

        return str(self._orderRef)

    # ----------------------------------------------------------------------
    def cancelOrder(self, instrumentID, orderID, frontID, sessionID):
        """撤单
        :param instrumentID: 合约号
        :param orderID: 订单号
        :param frontID: 前置机号
        :param sessionID: 会话ID

        :enum actionFlag: 操作标志
            - 删除 THOST_FTDC_AF_Delete '0'
            - 修改 THOST_FTDC_AF_Modify '3'
        """

        # 使用 frontID, sessionID, orderID三元组
        inputOrderActionField = InputOrderActionField()
        inputOrderActionField.brokerID = self._brokerID
        inputOrderActionField.investorID = self._userID
        inputOrderActionField.actionFlag = '0'
        inputOrderActionField.instrumentID = instrumentID
        inputOrderActionField.orderRef = orderID
        inputOrderActionField.frontID = frontID
        inputOrderActionField.sessionID = sessionID
        self._requestId += 1
        self.reqOrderAction(inputOrderActionField, self._requestId)

    def onRtnOrder(self, OrderField):
        """报单通知"""
        # #如果委托成功，OrderSubmitStatus先是0（不用管），则OrderSubmitStatus = 3，且orderStatus = 3，等待排队.
        #               紧接着成交则OrderSubmitStatus = 3，且orderStatus = 0-1
        ## 如果撤单成功，OrderSubmitStatus先是1（不用管），则OrderSubmitStatus = 3，且orderStatus = *.等待撤单
        #               紧接着成交则OrderSubmitStatus = 3，且orderStatus = 5 ？？

        print u"报单通知，limitPrice:{0}, orderRef: {1}, sessionID: {2}, frontID: {3}, notifySequence: {4}, " \
              u"orderStatus: {5}, orderSubmitStatus: {6}".format(OrderField.limitPrice, OrderField.orderRef,
                                                                 OrderField.sessionID, OrderField.frontID,
                                                                 OrderField.notifySequence, OrderField.orderStatus,
                                                                 OrderField.orderSubmitStatus)

    def onRspOrderAction(self, InputOrderActionField, RspInfoField, requestId, final):
        """报单操作请求响应"""
        print(
            u"onRspOrderAction --- sessionId: {0}, frontID: {1}, orderRef: {2}".format(InputOrderActionField.sessionID,
                                                                                       InputOrderActionField.frontID,
                                                                                       InputOrderActionField.orderRef))
        print(u"onRspOrderAction --- errorCode:{0}, errorMsg:{1}.".format(
            RspInfoField.errorID, RspInfoField.errorMsg.decode('gbk')))


if __name__ == "__main__":
    """
    :enum orderSubmitStatus: 报单提交状态
        - 已经提交 THOST_FTDC_OSS_InsertSubmitted '0'
        - 撤单已经提交 THOST_FTDC_OSS_CancelSubmitted '1'
        - 修改已经提交 THOST_FTDC_OSS_ModifySubmitted '2'
        - 已经接受 THOST_FTDC_OSS_Accepted '3'
        - 报单已经被拒绝 THOST_FTDC_OSS_InsertRejected '4'
        - 撤单已经被拒绝 THOST_FTDC_OSS_CancelRejected '5'
        - 改单已经被拒绝 THOST_FTDC_OSS_ModifyRejected '6'

    :enum orderStatus: 报单状态
        - 全部成交 THOST_FTDC_OST_AllTraded '0'
        - 部分成交还在队列中 THOST_FTDC_OST_PartTradedQueueing '1'
        - 部分成交不在队列中 THOST_FTDC_OST_PartTradedNotQueueing '2'
        - 未成交还在队列中 THOST_FTDC_OST_NoTradeQueueing '3'
        - 未成交不在队列中 THOST_FTDC_OST_NoTradeNotQueueing '4'
        - 撤单 THOST_FTDC_OST_Canceled '5'
        - 未知 THOST_FTDC_OST_Unknown 'a'
        - 尚未触发 THOST_FTDC_OST_NotTouched 'b'
        - 已触发 THOST_FTDC_OST_Touched 'c'
    """
    sgitTd = SgitTd("./")

    sgitTd.login(*deploy['TD'])

    # orderRef = sgitTd.sendOrder("cu1707", "0", "2", "0", 2000, 1)
    # time.sleep(5)
    # sgitTd.reqQryOrder()
    # for i in range(100):
    #     print 'test'
    #     time.sleep(0.5)
    # sgitTd.cancelOrder("cu1707", orderRef, sgitTd.frontID, sgitTd.sessionID)
    sgitTd.join()
