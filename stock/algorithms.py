#!/usr/bin/env python3
import logging
import pickle
import random
from . import models
from os.path import realpath, dirname, join


logger = logging.getLogger('algorithms')

in_algorithm_list = []
out_algorithm_list = []


CONSERVATIVE = 0
MODERATE = 1
AGGRESSIVE = 2          # more frequent trading


def buy_all(stock):
    budget = stock.account.cash_to_trade
    if budget > stock.budget:
        budget = stock.budget

    return budget / stock.value


def sell_all(stock):
    return -stock.count


class TradeAlgorithm:
    name = None

    def trade_decision(self, stock, time_now=None):
        return 0


trend_variables = [
    {'up_count': 4, 'down_count': 4, 'pause_count': 5},  # conservative
    {'up_count': 3, 'down_count': 3, 'pause_count': 4},  # moderate
    {'up_count': 2, 'down_count': 2, 'pause_count': 3},  # aggressive
]
MIN_HISTORY = 10


class MonkeyAlgorithm(TradeAlgorithm):
    name = 'Monkey'

    def trade_decision(self, stock):
        logger.debug('kikikik')
        val = random.random()
        if not stock.count and val > 0.85:
            logger.debug('buy all')
            return buy_all(stock)

        if stock.count and val > 0.85:
            logger.debug('sell all')
            return -stock.count

        return 0


in_algorithm_list.append(MonkeyAlgorithm)
out_algorithm_list.append(MonkeyAlgorithm)


class FillAlgorithm(TradeAlgorithm):
    name = 'Fill'

    def trade_decision(self, stock):
        total_value = stock.get_total_value()
        if total_value is None:
            logger.error('huh total value of stock is None : symbol %s' % stock.symbol)
            return 0
        overflow = total_value - stock.budget

        logger.debug('fill: total_value - %f' % total_value)
        logger.debug('fill: overflow - %f' % overflow)

        return -overflow / stock.value

in_algorithm_list.append(FillAlgorithm)


class EmptyAlgorithm(TradeAlgorithm):
    name = 'Empty'

    def trade_decision(self, stock):
        if stock.count:
            return sell_all(stock)

        return 0

out_algorithm_list.append(EmptyAlgorithm)


class HoldAlgorithm(TradeAlgorithm):
    name = 'Hold'

    def trade_decision(self, stock):
        return 0

in_algorithm_list.append(HoldAlgorithm)
out_algorithm_list.append(HoldAlgorithm)


up_variables = (
    {'consecutive_up': 5},
    {'consecutive_up': 3},
    {'consecutive_up': 2},
)

class UpAlgorithm(TradeAlgorithm):
    name = 'ConsecutiveUp'

    def trade_decision(self, stock):
        if stock.count:
            return 0

        consecutive_up = up_variables[stock.in_stance]['consecutive_up']

        logger.debug('evaluating: %s' % stock.symbol)

        try:
            histories = models.DayHistory.objects.filter(symbol=stock.symbol).order_by('-date')[0:consecutive_up]
        except IndexError:
            logger.info('not enough history yet')
            return 0

        for i in range(len(histories) - 1):
            if histories[i].open < histories[i+1].open:
                return 0

        return buy_all(stock)

in_algorithm_list.append(UpAlgorithm)


ahnyung_variable = (
    {'out_rate': 1.100},
    {'out_rate': 1.050},
    {'out_rate': 1.030},
)

class AhnyungAlgorithm(TradeAlgorithm):
    name = "Anhyung"

    def trade_decision(self, stock):
        if not stock.count:
            return 0

        out_rate = ahnyung_variable[stock.out_stance]['out_rate']

        logger.debug('evaluating: %s' % stock.symbol)

        try:
            order = models.Order.objects.filter(
                symbol=stock.symbol,
                account_id=stock.account.id,
                action=models.ACTION_BUY).order_by('-dt')[0]
        except IndexError:
            logger.info('there is no order information yet')
            return 0

        print(stock.value)

        if order.price < (stock.value * out_rate):
            return sell_all(stock)

        return 0

out_algorithm_list.append(AhnyungAlgorithm)

