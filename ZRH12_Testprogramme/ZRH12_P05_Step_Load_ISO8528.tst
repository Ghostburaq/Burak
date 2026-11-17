'    ZRH12 WINTERTHUR - ENERIA CAT 3516, 3.5 MVA / approx 2800 kW at 0.8 pf
'    Aggreko orders A766406 (54 x 200 kW) and A766407 (6 MVA)
'    P05 - STEP LOAD ACCEPTANCE AND REJECTION TO ISO 8528-5, Rev 1
'    Aggreko / Mobil in Time AG - B. Uecoez
'
'    PURPOSE
'      Prove generator transient performance under step load application and step
'      load rejection, recorded for the Level 4 test report.
'
'    WHY THIS PROGRAMME EXISTS
'      ISO 8528-5 evaluates load acceptance as block load steps and load rejection
'      as removal of 100 percent of rated load in one step. It does not define a
'      continuous kW per second ramp rate. A resistive load bank is a switched
'      device by construction, and Sigma PC is built to record the recovery times
'      and percentage deviations that ISO 8528 testing requires.
'      This programme is the normative counterpart to the project specific ramp in
'      P02. Both should be in the test file.
'
'    REFERENCE VALUE
'      100 percent = 2750 kW at the load bank, approximately 2800 kW at the
'      generator terminals once cable losses are added.
'
'    WHAT TO RECORD AT EVERY STEP
'      Voltage dip and recovery time, frequency dip and recovery time, overshoot on
'      rejection. Sigma PC records transient response data at each load change.
'      Compare against the ISO 8528-5 performance class agreed for this project.
'      G3 is the usual class where UPS and IT load dominate. Confirm the class in
'      the project specification before the run and enter it in the test sheet.
'
'    SECTION 5 NOTE
'      A 110 percent overload step is deliberately NOT included. It is run only on
'      written release from the generator supplier and with the load bank rating
'      confirmed for that point.
'    Expected total run time: 35 min 42 s
'
Capture  On
Section  Heatrun
Instrumentation  Full
'
'    SECTION 0 - defined start state
'      Fans running, zero load, 60 s settle before the first step.
'      Confirm bank temperature state and record it in the test sheet.
Load  0kw 1cosÿ 00:00:00 No
Delay  00:01:00
'
'    SECTION 1 - progressive load acceptance, 4 blocks
'      0 to 25 to 50 to 75 to 100 percent, 120 s on each block.
'      Each transition is a single step, applied from a settled condition.
Load  687.5kw 1cosÿ 00:00:00 No
Delay  00:02:00
Load  1375kw 1cosÿ 00:00:00 No
Delay  00:02:00
Load  2062.5kw 1cosÿ 00:00:00 No
Delay  00:02:00
Load  2750kw 1cosÿ 00:00:00 No
Delay  00:02:00
'
'    SECTION 2 - full load rejection, 100 to 0 percent in one step
'      ISO 8528-5 defines load rejection as removal of 100 percent in one step.
'      Record voltage overshoot and settling time. 180 s recovery before the next block.
Load  0kw 1cosÿ 00:00:00 No
Delay  00:03:00
'
'    SECTION 3 - single block acceptance from no load
'      Each block applied from zero, the hardest case for the governor and AVR.
'      Return to zero and settle 120 s between blocks.
Load  687.5kw 1cosÿ 00:00:00 No
Delay  00:01:30
Load  0kw 1cosÿ 00:00:00 No
Delay  00:02:00
Load  1375kw 1cosÿ 00:00:00 No
Delay  00:01:30
Load  0kw 1cosÿ 00:00:00 No
Delay  00:02:00
Load  2062.5kw 1cosÿ 00:00:00 No
Delay  00:01:30
Load  0kw 1cosÿ 00:00:00 No
Delay  00:02:00
Load  2750kw 1cosÿ 00:00:00 No
Delay  00:01:30
Load  0kw 1cosÿ 00:00:00 No
Delay  00:02:00
'
'    SECTION 4 - stepped rejection, 100 to 75 to 50 to 25 to 0 percent
'      Descending single steps, 90 s on each, to record rejection behaviour
'      at partial load as well as at full load.
Load  2750kw 1cosÿ 00:00:00 No
Delay  00:02:00
Load  2062.5kw 1cosÿ 00:00:00 No
Delay  00:01:30
Load  1375kw 1cosÿ 00:00:00 No
Delay  00:01:30
Load  687.5kw 1cosÿ 00:00:00 No
Delay  00:01:30
'
'    SECTION 5 - cool-down
'      Zero load with fans running for 180 s before shutdown, so the
'      elements are not left hot with the fans stopped.
Load  0kw 1cosÿ 00:00:00 No
Delay  00:03:00
Reject
Capture  Off
