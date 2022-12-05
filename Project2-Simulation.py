#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 09:00:51 2022

@author: nhungochoang
@author: sarahnguyen
"""
 
import simpy
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

class Customer:

    def __init__(self, number, env, stations, payment_space, pickup_space):
        self.custNo = number
        self.env = env
        self.stations = stations
        self.payment_space = payment_space
        self.pickup_space = pickup_space
   
    def pickShortestLine(self):
        stationNo = 0
        if stations[0].count < stations[0].capacity:
            stationNo = 0
        elif stations[1].count < stations[1].capacity:
            stationNo = 1
        elif len(stations[0].queue) < len(stations[1].queue):
            stationNo = 0
        else:
            stationNo = 1
        return stationNo
   
    def service(self):
        global served
        global totalCars
        # Picks shortest order line
        stationNo = self.pickShortestLine()
       
        # Order Station: requesting the order station
        print(f"customer{self.custNo} arrives at {env.now:7.3f}")
        totalCars += 1
        orderStationreq = stations[stationNo].request()
        yield orderStationreq
       
        # The time to place the order is defined by a lognormal distributed random variable with a mean order time of 30.2 seconds per order
        print(f"customer{self.custNo} starts placing orders at station #{stationNo} at {env.now:7.3f}")

        customerOrderTime = np.random.lognormal(np.log(30.2))
        averageOrderList.append(customerOrderTime)
        yield env.timeout(customerOrderTime)
                          
        # Requesting a space to get in payment window line
        print(f"customer{self.custNo} requests space to move forward at {env.now:7.3f}")    
        paymentspReq = payment_space.request()
        yield paymentspReq
        print(f"customer{self.custNo} acquires space to move forward at {env.now:7.3f}")  
       
        # releasing the order station
        self.stations[stationNo].release(orderStationreq)
        print(f"customer{self.custNo} finishes placing orders at station #{stationNo} at {env.now:7.3f}")
       
        # Payment Window: request the payment window
        paymentStationReq = stations[2].request()
        yield paymentStationReq
       
        # releasing the space so another car can move forward
        payment_space.release(paymentspReq)
        print(f"customer{self.custNo} releases space, moves forward, and starts picking up orders at {env.now:7.3f}")
       
        # The time for payment is described by a gamma distributed random variable with a mean preparation time of 10.4 seconds per order.
        customerPaymentTime = np.random.gamma(10.4)
        averagePaymentList.append(customerPaymentTime)
        yield env.timeout(customerPaymentTime)
       
        # Requesting a space to get in pickup window line
        print(f"customer{self.custNo} requests space to move forward at {env.now:7.3f}")    
        pickupspReq = pickup_space.request()
        yield pickupspReq
        print(f"customer{self.custNo} acquires space to move forward at {env.now:7.3f}")  
       
        # releasing the payment window
        self.stations[2].release(paymentStationReq)
        print(f"customer{self.custNo} finishes paying at {env.now:7.3f}")
       
        # Pickup Window: request the pickup window
        pickupStationReq = stations[3].request()
        yield pickupStationReq
       
        # releasing the space so another car can move forward
        pickup_space.release(pickupspReq)
        print(f"customer{self.custNo} releases space, moves forward, and starts picking up orders at {env.now:7.3f}")
       
        # The time to collect the order is also determined by a lognormal distributed random variable with a mean of 24.1 seconds per order.
        customerPickupTime = np.random.lognormal(np.log(24.1))
        averagePickupList.append(customerPickupTime)
        yield env.timeout(customerPickupTime)
       
        # releasing the pick up window
        self.stations[3].release(pickupStationReq)
        print(f"customer{self.custNo} finishes picking up orders at {env.now:7.3f} and exits")
       
        served += 1

def customerGenerator(env, stations, payment_space, pickup_space):

    custNo = 0
   
    while True:
        cust = Customer(custNo, env, stations, payment_space, pickup_space)
        env.process(cust.service())
        custNo += 1
       
        # Arrival time is an exponential distributed random variable with a mean order time of  55.2 seconds per order
        custArrivalTime = np.random.exponential(55.2)
        averageArrivalList.append(custArrivalTime)
        yield env.timeout(custArrivalTime) #--customer randomly arrive in every 55.2 time units
 
averageThroughputList = []
averageArrivalList = []
averageOrderList = []
averagePaymentList = []
averagePickupList = []

for replicate in range(100):
    served = 0
    totalCars = 0
    env = simpy.Environment()
   
    # 2 order stations, 1 payment window, 1 pick-up window
    stations = [simpy.Resource(env, capacity=6), simpy.Resource(env, capacity=6), simpy.Resource(env, capacity=1), simpy.Resource(env, capacity=1)]
    # 3 spaces between order and payment
    payment_space = simpy.Resource(env, capacity=3)
    # 1 space between payment and pickup
    pickup_space = simpy.Resource(env, capacity=1)
   
    env.process(customerGenerator(env, stations, payment_space, pickup_space))
    #simulate 30min = 1800  seconds
    env.run(until=1800)
   
    averageThroughput = served
    averageThroughputList.append(averageThroughput)
    print(f"Throughput: Number of cars that went through the facility: {served}")
   
#print(averageThroughputList)
print(f"Throughput average: The average number of cars that went through the facility: {np.average(averageThroughputList):0.3}")

plt.figure()
plt.bar(range(len(averageThroughputList)), averageThroughputList)
plt.xlabel("Experimental replicate")
plt.ylabel("Number served")
plt.title("Number served customers per experimental replicate")
 
# Caculate Confidence Interval
sampleMean = np.mean(averageThroughputList)
sampleDev = np.var(averageThroughputList, ddof=1)

sampleStdError = stats.sem(averageThroughputList)
degreesFreedom = len(averageThroughputList) - 1
interval = stats.t.interval(alpha = 0.90, loc = sampleMean, df = degreesFreedom, scale = sampleStdError)
 

print(f'sample mean = {sampleMean : 0.3f} sample variance = {sampleDev : 0.3f}')
print("confidence interval = ", interval)

print(f'mean arival time = {np.mean(averageArrivalList) : 0.3f} with variance = {np.var(averageArrivalList, ddof=1) : 0.3f}')
print(f'mean order time = {np.mean(averageOrderList) : 0.3f} with variance = {np.var(averageOrderList, ddof=1) : 0.3f}')
print(f'mean payment time = {np.mean(averagePaymentList) : 0.3f} with variance = {np.var(averagePaymentList, ddof=1) : 0.3f}')
print(f'mean pickup time = {np.mean(averagePickupList) : 0.3f} with variance = {np.var(averagePickupList, ddof=1) : 0.3f}')
