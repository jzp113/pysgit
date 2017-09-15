#include "sgitmd.h"

SgitMd::SgitMd(const std::string &szFlowPath, bool usingUdp, bool multicast) {
    this->api = CThostFtdcMdApi::CreateFtdcMdApi(szFlowPath.c_str(), usingUdp, multicast);
    boost::function0<void> f = boost::bind(&SgitMd::processTask, this);
    this->task_thread = new boost::thread(f);
}

SgitMd::~SgitMd() {
    task_thread->interrupt();
    task_thread->join();
    delete task_thread;
    this->api->Release();
}

void SgitMd::OnFrontConnected() {
    Task *task = new Task();
    task->name = ON_FRONT_CONNECTED;
    this->task_queue.push(task);
}

void SgitMd::OnFrontDisconnected(int nReason) {
    Task *task = new Task();
    task->name = ON_FRONT_DISCONNECTED;
    task->num = nReason;
    this->task_queue.push(task);
}

void SgitMd::OnHeartBeatWarning(int nTimeLapse) {
    Task *task = new Task();
    task->name = ON_HEART_BEAT_WARNING;
    task->num = nTimeLapse;
    this->task_queue.push(task);
}

void SgitMd::OnRspUserLogin(CThostFtdcRspUserLoginField *pRspUserLogin, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) {
    Task *task = new Task();
    task->name = ON_RSP_USER_LOGIN;
    if (pRspUserLogin)
        task->payload = RspUserLoginField(*pRspUserLogin);
    if (pRspInfo)
        task->resp = RspInfoField(*pRspInfo);
    task->num = nRequestID;
    task->final = bIsLast;
    this->task_queue.push(task);
}

void SgitMd::OnRspUserLogout(CThostFtdcUserLogoutField *pUserLogout, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) {
    Task *task = new Task();
    task->name = ON_RSP_USER_LOGOUT;
    if (pUserLogout)
        task->payload = UserLogoutField(*pUserLogout);
    if (pRspInfo)
        task->resp = RspInfoField(*pRspInfo);
    task->num = nRequestID;
    task->final = bIsLast;
    this->task_queue.push(task);
}

void SgitMd::OnRspError(CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) {
    Task *task = new Task();
    task->name = ON_RSP_ERROR;
    if (pRspInfo)
        task->resp = RspInfoField(*pRspInfo);
    task->num = nRequestID;
    task->final = bIsLast;
    this->task_queue.push(task);
}

void SgitMd::OnRspSubMarketData(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) {
    Task *task = new Task();
    task->name = ON_RSP_SUB_MARKET_DATA;
    if (pSpecificInstrument)
        task->payload = SpecificInstrumentField(*pSpecificInstrument);
    if (pRspInfo)
        task->resp = RspInfoField(*pRspInfo);
    task->num = nRequestID;
    task->final = bIsLast;
    this->task_queue.push(task);
}

void SgitMd::OnRspUnSubMarketData(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) {
    Task *task = new Task();
    task->name = ON_RSP_UN_SUB_MARKET_DATA;
    if (pSpecificInstrument)
        task->payload = SpecificInstrumentField(*pSpecificInstrument);
    if (pRspInfo)
        task->resp = RspInfoField(*pRspInfo);
    task->num = nRequestID;
    task->final = bIsLast;
    this->task_queue.push(task);
}

void SgitMd::OnRspSubForQuoteRsp(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) {
    Task *task = new Task();
    task->name = ON_RSP_SUB_FOR_QUOTE_RSP;
    if (pSpecificInstrument)
        task->payload = SpecificInstrumentField(*pSpecificInstrument);
    if (pRspInfo)
        task->resp = RspInfoField(*pRspInfo);
    task->num = nRequestID;
    task->final = bIsLast;
    this->task_queue.push(task);
}

void SgitMd::OnRspUnSubForQuoteRsp(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) {
    Task *task = new Task();
    task->name = ON_RSP_UN_SUB_FOR_QUOTE_RSP;
    if (pSpecificInstrument)
        task->payload = SpecificInstrumentField(*pSpecificInstrument);
    if (pRspInfo)
        task->resp = RspInfoField(*pRspInfo);
    task->num = nRequestID;
    task->final = bIsLast;
    this->task_queue.push(task);
}

void SgitMd::OnRtnDepthMarketData(CThostFtdcDepthMarketDataField *pDepthMarketData) {
    Task *task = new Task();
    task->name = ON_RTN_DEPTH_MARKET_DATA;
    if (pDepthMarketData)
        task->payload = DepthMarketDataField(*pDepthMarketData);
    this->task_queue.push(task);
}

void SgitMd::OnRtnForQuoteRsp(CThostFtdcForQuoteRspField *pForQuoteRsp) {
    Task *task = new Task();
    task->name = ON_RTN_FOR_QUOTE_RSP;
    if (pForQuoteRsp)
        task->payload = ForQuoteRspField(*pForQuoteRsp);
    this->task_queue.push(task);
}

void SgitMd::processTask() {
    while (true) {
        Task* task = this->task_queue.wait_and_pop();
        WithdrawGIL lock;
        switch (task->name) {
            case ON_FRONT_CONNECTED: {
                this->onFrontConnected();
                break;
            }
            case ON_FRONT_DISCONNECTED: {
                this->onFrontDisconnected(task->num);
                break;
            }
            case ON_HEART_BEAT_WARNING: {
                this->onHeartBeatWarning(task->num);
                break;
            }
            case ON_RSP_USER_LOGIN: {
                const object &payload = task->payload.empty() ? object() : object(any_cast<RspUserLoginField &>(task->payload));
                const object &resp = task->resp.empty() ? object() : object(any_cast<RspInfoField &>(task->resp));
                this->onRspUserLogin(const_cast<object &>(payload), const_cast<object &>(resp), task->num, task->final);
                break;
            }
            case ON_RSP_USER_LOGOUT: {
                const object &payload = task->payload.empty() ? object() : object(any_cast<UserLogoutField &>(task->payload));
                const object &resp = task->resp.empty() ? object() : object(any_cast<RspInfoField &>(task->resp));
                this->onRspUserLogout(const_cast<object &>(payload), const_cast<object &>(resp), task->num, task->final);
                break;
            }
            case ON_RSP_ERROR: {
                const object &resp = task->resp.empty() ? object() : object(any_cast<RspInfoField &>(task->resp));
                this->onRspError(const_cast<object &>(resp), task->num, task->final);
                break;
            }
            case ON_RSP_SUB_MARKET_DATA: {
                const object &payload = task->payload.empty() ? object() : object(any_cast<SpecificInstrumentField &>(task->payload));
                const object &resp = task->resp.empty() ? object() : object(any_cast<RspInfoField &>(task->resp));
                this->onRspSubMarketData(const_cast<object &>(payload), const_cast<object &>(resp), task->num, task->final);
                break;
            }
            case ON_RSP_UN_SUB_MARKET_DATA: {
                const object &payload = task->payload.empty() ? object() : object(any_cast<SpecificInstrumentField &>(task->payload));
                const object &resp = task->resp.empty() ? object() : object(any_cast<RspInfoField &>(task->resp));
                this->onRspUnSubMarketData(const_cast<object &>(payload), const_cast<object &>(resp), task->num, task->final);
                break;
            }
            case ON_RSP_SUB_FOR_QUOTE_RSP: {
                const object &payload = task->payload.empty() ? object() : object(any_cast<SpecificInstrumentField &>(task->payload));
                const object &resp = task->resp.empty() ? object() : object(any_cast<RspInfoField &>(task->resp));
                this->onRspSubForQuoteRsp(const_cast<object &>(payload), const_cast<object &>(resp), task->num, task->final);
                break;
            }
            case ON_RSP_UN_SUB_FOR_QUOTE_RSP: {
                const object &payload = task->payload.empty() ? object() : object(any_cast<SpecificInstrumentField &>(task->payload));
                const object &resp = task->resp.empty() ? object() : object(any_cast<RspInfoField &>(task->resp));
                this->onRspUnSubForQuoteRsp(const_cast<object &>(payload), const_cast<object &>(resp), task->num, task->final);
                break;
            }
            case ON_RTN_DEPTH_MARKET_DATA: {
                const object &payload = task->payload.empty() ? object() : object(any_cast<DepthMarketDataField &>(task->payload));
                this->onRtnDepthMarketData(const_cast<object &>(payload));
                break;
            }
            case ON_RTN_FOR_QUOTE_RSP: {
                const object &payload = task->payload.empty() ? object() : object(any_cast<ForQuoteRspField &>(task->payload));
                this->onRtnForQuoteRsp(const_cast<object &>(payload));
                break;
            }
        }
        delete task;
    }
}

const char *SgitMd::getApiVersion() {
    return  CThostFtdcMdApi::GetApiVersion();
}

void SgitMd::release() {
    DepositGIL unlocker;
    this->api->Release();
}

void SgitMd::init() {
    DepositGIL unlocker;
    this->api->Init();
}

int SgitMd::join() {
    DepositGIL unlocker;
    return this->api->Join();
}

const char *SgitMd::getTradingDay() {
    return this->api->GetTradingDay();
}

void SgitMd::registerFront(const std::string &szFrontAddress) {
    this->api->RegisterFront(const_cast<char *>(szFrontAddress.c_str()));
}

void SgitMd::registerNameServer(const std::string &szNsAddress) {
    this->api->RegisterNameServer(const_cast<char *>(szNsAddress.c_str()));
}

void SgitMd::registerFensUserInfo(object &fensUserInfoField) {
    FensUserInfoField *p1 = extract<FensUserInfoField *>(fensUserInfoField);
    this->api->RegisterFensUserInfo(p1);
}

void SgitMd::registerSpi() {
    this->api->RegisterSpi(this);
}

int SgitMd::subscribeMarketData(list &instrumentIDs) {
    int length = len(instrumentIDs);
    char **array = new char*[length];
    for (int i = 0; i < length; i++) {
        *(array + i) = const_cast<char *>(extract<const char *>(instrumentIDs[i])());
    };
    int result = this->api->SubscribeMarketData(array, length);
    delete array;
    return result;
}

int SgitMd::unSubscribeMarketData(list &instrumentIDs) {
    int length = len(instrumentIDs);
    char **array = new char*[length];
    for (int i = 0; i < length; i++) {
        *(array + i) = const_cast<char *>(extract<const char *>(instrumentIDs[i])());
    };
    int result = this->api->UnSubscribeMarketData(array, length);
    delete array;
    return result;
}

int SgitMd::subscribeForQuoteRsp(list &instrumentIDs) {
    int length = len(instrumentIDs);
    char **array = new char*[length];
    for (int i = 0; i < length; i++) {
        *(array + i) = const_cast<char *>(extract<const char *>(instrumentIDs[i])());
    };
    int result = this->api->SubscribeForQuoteRsp(array, length);
    delete array;
    return result;
}

int SgitMd::unSubscribeForQuoteRsp(list &instrumentIDs) {
    int length = len(instrumentIDs);
    char **array = new char*[length];
    for (int i = 0; i < length; i++) {
        *(array + i) = const_cast<char *>(extract<const char *>(instrumentIDs[i])());
    };
    int result = this->api->UnSubscribeForQuoteRsp(array, length);
    delete array;
    return result;
}

int SgitMd::reqUserLogin(object &reqUserLoginField, int requestId) {
    ReqUserLoginField *p1 = extract<ReqUserLoginField *>(reqUserLoginField);
    return this->api->ReqUserLogin(p1, requestId);
}

int SgitMd::reqUserLogout(object &userLogoutField, int requestId) {
    UserLogoutField *p1 = extract<UserLogoutField *>(userLogoutField);
    return this->api->ReqUserLogout(p1, requestId);
}

struct SgitMdWrap : SgitMd, wrapper<SgitMd> {

    SgitMdWrap(const std::string &szFlowPath = "", bool usingUdp=false, bool multicast=false)
            : SgitMd(szFlowPath, usingUdp, multicast) {}

    virtual void onFrontConnected() {
        try {
            this->get_override("onFrontConnected")();
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };

    virtual void onFrontDisconnected(int reasonCode) {
        try {
            this->get_override("onFrontDisconnected")(reasonCode);
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };

    virtual void onHeartBeatWarning(int lapsedTime) {
        try {
            this->get_override("onHeartBeatWarning")(lapsedTime);
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };

    virtual void onRspUserLogin(object &rspUserLoginField, object &rspInfoField, int requestId, bool final) {
        try {
            this->get_override("onRspUserLogin")(rspUserLoginField, rspInfoField, requestId, final);
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };

    virtual void onRspUserLogout(object &userLogoutField, object &rspInfoField, int requestId, bool final) {
        try {
            this->get_override("onRspUserLogout")(userLogoutField, rspInfoField, requestId, final);
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };

    virtual void onRspError(object &rspInfoField, int requestId, bool final) {
        try {
            this->get_override("onRspError")(rspInfoField, requestId, final);
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };

    virtual void onRspSubMarketData(object &specificInstrumentField, object &rspInfoField, int requestId, bool final) {
        try {
            this->get_override("onRspSubMarketData")(specificInstrumentField, rspInfoField, requestId, final);
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };

    virtual void onRspUnSubMarketData(object &specificInstrumentField, object &rspInfoField, int requestId, bool final) {
        try {
            this->get_override("onRspUnSubMarketData")(specificInstrumentField, rspInfoField, requestId, final);
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };

    virtual void onRspSubForQuoteRsp(object &specificInstrumentField, object &rspInfoField, int requestId, bool final) {
        try {
            this->get_override("onRspSubForQuoteRsp")(specificInstrumentField, rspInfoField, requestId, final);
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };

    virtual void onRspUnSubForQuoteRsp(object &specificInstrumentField, object &rspInfoField, int requestId, bool final) {
        try {
            this->get_override("onRspUnSubForQuoteRsp")(specificInstrumentField, rspInfoField, requestId, final);
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };

    virtual void onRtnDepthMarketData(object &depthMarketDataField) {
        try {
            this->get_override("onRtnDepthMarketData")(depthMarketDataField);
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };

    virtual void onRtnForQuoteRsp(object &forQuoteRspField) {
        try {
            this->get_override("onRtnForQuoteRsp")(forQuoteRspField);
        } catch (error_already_set const &) {
            PyErr_Print();
        }
    };
};

BOOST_PYTHON_MODULE(sgitmd) {
    if (!PyEval_ThreadsInitialized())
        PyEval_InitThreads();	//导入时运行，保证先创建GIL

    class_<SgitMdWrap, boost::noncopyable>("SgitMd", init<const std::string &, bool, bool>())
            .def("onFrontConnected", pure_virtual(&SgitMdWrap::onFrontConnected))
            .def("onFrontDisconnected", pure_virtual(&SgitMdWrap::onFrontDisconnected))
            .def("onHeartBeatWarning", pure_virtual(&SgitMdWrap::onHeartBeatWarning))
            .def("onRspUserLogin", pure_virtual(&SgitMdWrap::onRspUserLogin))
            .def("onRspUserLogout", pure_virtual(&SgitMdWrap::onRspUserLogout))
            .def("onRspError", pure_virtual(&SgitMdWrap::onRspError))
            .def("onRspSubMarketData", pure_virtual(&SgitMdWrap::onRspSubMarketData))
            .def("onRspUnSubMarketData", pure_virtual(&SgitMdWrap::onRspUnSubMarketData))
            .def("onRspSubForQuoteRsp", pure_virtual(&SgitMdWrap::onRspSubForQuoteRsp))
            .def("onRspUnSubForQuoteRsp", pure_virtual(&SgitMdWrap::onRspUnSubForQuoteRsp))
            .def("onRtnDepthMarketData", pure_virtual(&SgitMdWrap::onRtnDepthMarketData))
            .def("onRtnForQuoteRsp", pure_virtual(&SgitMdWrap::onRtnForQuoteRsp))
            .def("getApiVersion", &SgitMdWrap::getApiVersion)
            .def("release", &SgitMdWrap::release)
            .def("init", &SgitMdWrap::init)
            .def("join", &SgitMdWrap::join)
            .def("getTradingDay", &SgitMdWrap::getTradingDay)
            .def("registerFront", &SgitMdWrap::registerFront)
            .def("registerNameServer", &SgitMdWrap::registerNameServer)
            .def("registerFensUserInfo", &SgitMdWrap::registerFensUserInfo)
            .def("registerSpi", &SgitMdWrap::registerSpi)
            .def("subscribeMarketData", &SgitMdWrap::subscribeMarketData)
            .def("unSubscribeMarketData", &SgitMdWrap::unSubscribeMarketData)
            .def("subscribeForQuoteRsp", &SgitMdWrap::subscribeForQuoteRsp)
            .def("unSubscribeForQuoteRsp", &SgitMdWrap::unSubscribeForQuoteRsp)
            .def("reqUserLogin", &SgitMdWrap::reqUserLogin)
            .def("reqUserLogout", &SgitMdWrap::reqUserLogout);


    class_<ReqUserLoginField>("ReqUserLoginField")
            .add_property("tradingDay", &ReqUserLoginField::getTradingDay, &ReqUserLoginField::setTradingDay)
            .add_property("brokerID", &ReqUserLoginField::getBrokerID, &ReqUserLoginField::setBrokerID)
            .add_property("userID", &ReqUserLoginField::getUserID, &ReqUserLoginField::setUserID)
            .add_property("password", &ReqUserLoginField::getPassword, &ReqUserLoginField::setPassword)
            .add_property("userProductInfo", &ReqUserLoginField::getUserProductInfo, &ReqUserLoginField::setUserProductInfo)
            .add_property("interfaceProductInfo", &ReqUserLoginField::getInterfaceProductInfo, &ReqUserLoginField::setInterfaceProductInfo)
            .add_property("protocolInfo", &ReqUserLoginField::getProtocolInfo, &ReqUserLoginField::setProtocolInfo)
            .add_property("macAddress", &ReqUserLoginField::getMacAddress, &ReqUserLoginField::setMacAddress)
            .add_property("oneTimePassword", &ReqUserLoginField::getOneTimePassword, &ReqUserLoginField::setOneTimePassword)
            .add_property("clientIPAddress", &ReqUserLoginField::getClientIPAddress, &ReqUserLoginField::setClientIPAddress);

    class_<RspUserLoginField>("RspUserLoginField")
            .add_property("tradingDay", &RspUserLoginField::getTradingDay, &RspUserLoginField::setTradingDay)
            .add_property("loginTime", &RspUserLoginField::getLoginTime, &RspUserLoginField::setLoginTime)
            .add_property("brokerID", &RspUserLoginField::getBrokerID, &RspUserLoginField::setBrokerID)
            .add_property("userID", &RspUserLoginField::getUserID, &RspUserLoginField::setUserID)
            .add_property("systemName", &RspUserLoginField::getSystemName, &RspUserLoginField::setSystemName)
            .def_readwrite("frontID", &RspUserLoginField::FrontID)
            .def_readwrite("sessionID", &RspUserLoginField::SessionID)
            .add_property("maxOrderRef", &RspUserLoginField::getMaxOrderRef, &RspUserLoginField::setMaxOrderRef)
            .add_property("SHFETime", &RspUserLoginField::getSHFETime, &RspUserLoginField::setSHFETime)
            .add_property("DCETime", &RspUserLoginField::getDCETime, &RspUserLoginField::setDCETime)
            .add_property("CZCETime", &RspUserLoginField::getCZCETime, &RspUserLoginField::setCZCETime)
            .add_property("FFEXTime", &RspUserLoginField::getFFEXTime, &RspUserLoginField::setFFEXTime)
            .add_property("INETime", &RspUserLoginField::getINETime, &RspUserLoginField::setINETime);

    class_<UserLogoutField>("UserLogoutField")
            .add_property("brokerID", &UserLogoutField::getBrokerID, &UserLogoutField::setBrokerID)
            .add_property("userID", &UserLogoutField::getUserID, &UserLogoutField::setUserID);

    class_<RspInfoField>("RspInfoField")
            .def_readwrite("errorID", &RspInfoField::ErrorID)
            .add_property("errorMsg", &RspInfoField::getErrorMsg, &RspInfoField::setErrorMsg);

    class_<DepthMarketDataField>("DepthMarketDataField")
            .add_property("tradingDay", &DepthMarketDataField::getTradingDay, &DepthMarketDataField::setTradingDay)
            .add_property("instrumentID", &DepthMarketDataField::getInstrumentID, &DepthMarketDataField::setInstrumentID)
            .add_property("exchangeID", &DepthMarketDataField::getExchangeID, &DepthMarketDataField::setExchangeID)
            .add_property("exchangeInstID", &DepthMarketDataField::getExchangeInstID, &DepthMarketDataField::setExchangeInstID)
            .def_readwrite("lastPrice", &DepthMarketDataField::LastPrice)
            .def_readwrite("preSettlementPrice", &DepthMarketDataField::PreSettlementPrice)
            .def_readwrite("preClosePrice", &DepthMarketDataField::PreClosePrice)
            .def_readwrite("preOpenInterest", &DepthMarketDataField::PreOpenInterest)
            .def_readwrite("openPrice", &DepthMarketDataField::OpenPrice)
            .def_readwrite("highestPrice", &DepthMarketDataField::HighestPrice)
            .def_readwrite("lowestPrice", &DepthMarketDataField::LowestPrice)
            .def_readwrite("volume", &DepthMarketDataField::Volume)
            .def_readwrite("turnover", &DepthMarketDataField::Turnover)
            .def_readwrite("openInterest", &DepthMarketDataField::OpenInterest)
            .def_readwrite("closePrice", &DepthMarketDataField::ClosePrice)
            .def_readwrite("settlementPrice", &DepthMarketDataField::SettlementPrice)
            .def_readwrite("upperLimitPrice", &DepthMarketDataField::UpperLimitPrice)
            .def_readwrite("lowerLimitPrice", &DepthMarketDataField::LowerLimitPrice)
            .def_readwrite("preDelta", &DepthMarketDataField::PreDelta)
            .def_readwrite("currDelta", &DepthMarketDataField::CurrDelta)
            .add_property("updateTime", &DepthMarketDataField::getUpdateTime, &DepthMarketDataField::setUpdateTime)
            .def_readwrite("updateMillisec", &DepthMarketDataField::UpdateMillisec)
            .def_readwrite("bidPrice1", &DepthMarketDataField::BidPrice1)
            .def_readwrite("bidVolume1", &DepthMarketDataField::BidVolume1)
            .def_readwrite("askPrice1", &DepthMarketDataField::AskPrice1)
            .def_readwrite("askVolume1", &DepthMarketDataField::AskVolume1)
            .def_readwrite("bidPrice2", &DepthMarketDataField::BidPrice2)
            .def_readwrite("bidVolume2", &DepthMarketDataField::BidVolume2)
            .def_readwrite("askPrice2", &DepthMarketDataField::AskPrice2)
            .def_readwrite("askVolume2", &DepthMarketDataField::AskVolume2)
            .def_readwrite("bidPrice3", &DepthMarketDataField::BidPrice3)
            .def_readwrite("bidVolume3", &DepthMarketDataField::BidVolume3)
            .def_readwrite("askPrice3", &DepthMarketDataField::AskPrice3)
            .def_readwrite("askVolume3", &DepthMarketDataField::AskVolume3)
            .def_readwrite("bidPrice4", &DepthMarketDataField::BidPrice4)
            .def_readwrite("bidVolume4", &DepthMarketDataField::BidVolume4)
            .def_readwrite("askPrice4", &DepthMarketDataField::AskPrice4)
            .def_readwrite("askVolume4", &DepthMarketDataField::AskVolume4)
            .def_readwrite("bidPrice5", &DepthMarketDataField::BidPrice5)
            .def_readwrite("bidVolume5", &DepthMarketDataField::BidVolume5)
            .def_readwrite("askPrice5", &DepthMarketDataField::AskPrice5)
            .def_readwrite("askVolume5", &DepthMarketDataField::AskVolume5)
            .def_readwrite("averagePrice", &DepthMarketDataField::AveragePrice)
            .add_property("actionDay", &DepthMarketDataField::getActionDay, &DepthMarketDataField::setActionDay);

    class_<ForQuoteRspField>("ForQuoteRspField")
            .add_property("tradingDay", &ForQuoteRspField::getTradingDay, &ForQuoteRspField::setTradingDay)
            .add_property("instrumentID", &ForQuoteRspField::getInstrumentID, &ForQuoteRspField::setInstrumentID)
            .add_property("forQuoteSysID", &ForQuoteRspField::getForQuoteSysID, &ForQuoteRspField::setForQuoteSysID)
            .add_property("forQuoteTime", &ForQuoteRspField::getForQuoteTime, &ForQuoteRspField::setForQuoteTime)
            .add_property("actionDay", &ForQuoteRspField::getActionDay, &ForQuoteRspField::setActionDay)
            .add_property("exchangeID", &ForQuoteRspField::getExchangeID, &ForQuoteRspField::setExchangeID);

    class_<SpecificInstrumentField>("SpecificInstrumentField")
            .add_property("instrumentID", &SpecificInstrumentField::getInstrumentID, &SpecificInstrumentField::setInstrumentID);

    class_<FensUserInfoField>("FensUserInfoField")
            .add_property("brokerID", &FensUserInfoField::getBrokerID, &FensUserInfoField::setBrokerID)
            .add_property("userID", &FensUserInfoField::getUserID, &FensUserInfoField::setUserID)
            .def_readwrite("loginMode", &FensUserInfoField::LoginMode);

}