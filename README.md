# airport-simulator
We assume that flights begin departing at midnight (time 00:00) on first day of simulation and end at midnight (time 24:00) on last day of simulation
We assume that demand is constant for all times during the day

pseudocode:



-- CODE STARTS HERE --
-- MAIN CLASS --

collect input variables from user (using a config file)
generate flights and store in COMMERCIAL_FLIGHT_DEPARTURE_QUEUE and PROVINCIAL_FLIGHT_DEPARTURE_QUEUE
generate passengers for each flight scheduled to take place during the simulation and store in COMMERCIAL_PASSENGERS_QUEUE and PROVINCIAL_PASSENGERS_QUEUE queue

loop [until # days simulated met]
    //NOTE: checks below must occur in the specified order
    check COMMERCIAL_PASSENGERS_QUEUE (passenger arrival time) -> (add to BUSINESS_CHECKIN_WAITING_QUEUE or COACH_CHECKIN_WAITING_QUEUE)
    check PROVINCIAL_PASSENGERS_QUEUE (passenger arrival time) -> (add to BUSINESS_CHECKIN_WAITING_QUEUE or COACH_CHECKIN_WAITING_QUEUE)
    check each CHECKIN_WAITING_QUEUE (counter finished serving current customer) -> (add to COMMERCIAL_SECURITY_WAITING_QUEUE or PROVINCIAL_SECURITY_WAITING_QUEUE)
    check each CHECKIN_WAITING_QUEUE (counter finished serving current customer) -> (add to COMMERCIAL_SECURITY_WAITING_QUEUE or PROVINCIAL_SECURITY_WAITING_QUEUE)
    check each COMMERCIAL_SECURITY_WAITING_QUEUE (counter finished serving current customer) -> (add to COMMERCIAL_GATE_WAITING_QUEUE)
    check each PROVINCIAL_SECURITY_WAITING_QUEUE (counter finished serving current customer) -> (add to PROVINCIAL_GATE_WAITING_LIST)
    check COMMERCIAL_FLIGHT_DEPARTURE_QUEUE (flight departure time) -> (remove eligible passengers from COMMERCIAL_GATE_WAITING_QUEUE)
    check PROVINCIAL_FLIGHT_DEPARTURE_QUEUE (flight departure time) -> (remove eligible passengers from PROVINCIAL_GATE_WAITING_LIST)
    //
    handle whichever queue has the earliest trigger time (advance simulation time to that time) -> (continue looping)

-- BELOW HANDLED IN SEPARATE CLASSES --

generating flights:
- take `#` commercial flights per day and generate departure times starting at 00:30 and ending at 23:30
- take `#` provincial flights per day and generate departure times starting at 00:00 and ending at 24:00

generating passengers:
- for commercial passengers 
  - generate random variates for arrival time (poisson, average arrival rate = 40 per hour)
  - generate random variates for if they have bags
  - generate random variates for `#` of bags
- for each commercial flight
  - generate random variates for arrival time
  - generate random variates for if they have bags
  - generate random variates for `#` of bags

-- CODE ENDS HERE --



input variables:
- chance a commuter seat is filled
- chance a provincial seat is filled
- `#` business check-in stations
- `#` coach check-in stations
- `#` commercial security screening stations [cant change]
- `#` provincial security screening stations [cant change]
- recommended time for commuter passengers to arrive
- recommended time for provincial passengers to arrive
- how many days to run the simulation
- `#` commuter flights per day
- `#` provincial flights per day
- flag: allow check-in desks to service all passenger types when their queue is empty
- flag: allow all check-in desks to service business class passengers first (optional)
