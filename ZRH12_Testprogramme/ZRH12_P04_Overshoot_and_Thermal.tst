'    ZRH12 WINTERTHUR - ENERIA CAT 3516, 3.5 MVA / approx 2800 kW at 0.8 pf
'    Aggreko orders A766406 (54 x 200 kW) and A766407 (6 MVA)
'    P04 - OVERSHOOT AND THERMAL CHARACTERISATION, Rev B
'    Aggreko / Mobil in Time AG - B. Uecoez
'
'    PURPOSE
'      Quantify the offset between the load bank set point and the generator reading,
'      and separate its two causes: cable losses and element temperature.
'      Replaces ZRH12 Ramp CHECKs and L3 transient.
'
'    WHAT THE PREVIOUS CHECK PROGRAMME DID AND WHY IT WAS NOT ENOUGH
'      It stepped 2750 / 2740 / 2730 / 2720 / 2710 / 2700 / 2650 kW with 20 s holds
'      to chase the overshoot by trial and error, and carried the note 'First Ramp
'      to 2750 to match exact 2800 level on Gen HMI'. That is an empirical offset
'      valid for one thermal state only. 20 s per step is far shorter than the
'      thermal time constant of the elements, which is in the order of minutes, so
'      every reading was taken during the transient.
'
'    WHAT THIS PROGRAMME DOES INSTEAD
'      Three holds of 300 s at the same 2750 kW set point, separated by returns to
'      zero. Each hold is long enough for the elements to approach thermal
'      equilibrium. Reading the power at 0 s and at 300 s of each hold gives the
'      temperature coefficient directly. Comparing hold 1 with hold 3 gives the
'      residual offset once the bank is fully soaked, and that residual is the
'      cable loss plus instrument error, which is the number that belongs in the
'      test report.
'
'    EXPECTED RESULT
'      Power at the start of hold 1 is the highest reading of the run.
'      Power at the end of hold 3 is the lowest and is the true steady state value.
'      Difference between them: measured on 9 November as 122 kW, 4.2 percent.
'      Cable losses at these lengths: roughly 1 percent of 2750 kW.
'
'    WHAT TO DO WITH IT
'      Once the steady state offset is known, the acceptance run sets the load bank
'      to the generator target minus that offset, with a stated bank temperature
'      precondition. That is a documented correction, not a note in a programme file.
'    Expected total run time: 30 min 30 s
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
'    SECTION 1 - soak hold 1 at 2750 kW, 300 s
'      Ramp in 16 steps, then hold 300 s. Record power at 0 s, 60 s and 300 s.
'      Return to zero and 120 s off-load before the next hold.
Load  187kw 1cosÿ 00:00:00 No
Delay  00:00:10
Load  347kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  507kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  668kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  828kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  988kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1148kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1308kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1468kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1629kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1789kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1949kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2109kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2269kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2430kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2590kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2750kw 1cosÿ 00:00:00 No
Delay  00:05:00
Load  2000kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1200kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  500kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  0kw 1cosÿ 00:00:00 No
Delay  00:02:00
'
'    SECTION 2 - soak hold 2 at 2750 kW, 300 s
'      Ramp in 16 steps, then hold 300 s. Record power at 0 s, 60 s and 300 s.
'      Return to zero and 120 s off-load before the next hold.
Load  187kw 1cosÿ 00:00:00 No
Delay  00:00:10
Load  347kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  507kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  668kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  828kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  988kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1148kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1308kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1468kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1629kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1789kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1949kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2109kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2269kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2430kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2590kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2750kw 1cosÿ 00:00:00 No
Delay  00:05:00
Load  2000kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1200kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  500kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  0kw 1cosÿ 00:00:00 No
Delay  00:02:00
'
'    SECTION 3 - soak hold 3 at 2750 kW, 300 s
'      Ramp in 16 steps, then hold 300 s. Record power at 0 s, 60 s and 300 s.
'      Return to zero and 120 s off-load before the next hold.
Load  187kw 1cosÿ 00:00:00 No
Delay  00:00:10
Load  347kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  507kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  668kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  828kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  988kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1148kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1308kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1468kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1629kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1789kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1949kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2109kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2269kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2430kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2590kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2750kw 1cosÿ 00:00:00 No
Delay  00:05:00
Load  2000kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1200kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  500kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  0kw 1cosÿ 00:00:00 No
Delay  00:02:00
'
'    SECTION 4 - low load reference at 1375 kW, 180 s
'      Half load with the bank fully soaked. The percentage offset here tells
'      whether the deviation scales with power, which points to cable losses,
'      or stays constant, which points to instrument calibration.
Load  187kw 1cosÿ 00:00:00 No
Delay  00:00:10
Load  336kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  484kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  632kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  781kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  930kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1078kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1226kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1375kw 1cosÿ 00:00:00 No
Delay  00:03:00
Load  800kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  300kw 1cosÿ 00:00:00 No
Delay  00:00:01
'
'    SECTION 5 - cool-down
'      Zero load with fans running for 180 s before shutdown, so the
'      elements are not left hot with the fans stopped.
Load  0kw 1cosÿ 00:00:00 No
Delay  00:03:00
Reject
Capture  Off
