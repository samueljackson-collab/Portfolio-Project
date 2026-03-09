# Quantum circuit output and baseline comparison

## Circuit output
- Ansatz: TwoLocal (RY rotations, CZ entanglement, 4 qubits, reps=1)
- Measurements: all qubits

```
        ┌──────────────────────────────────────────────────────────────────┐ ░ »
   q_0: ┤0                                                                 ├─░─»
        │                                                                  │ ░ »
   q_1: ┤1                                                                 ├─░─»
        │  TwoLocal(0.1,0.22857,0.35714,0.48571,0.61429,0.74286,0.87143,1) │ ░ »
   q_2: ┤2                                                                 ├─░─»
        │                                                                  │ ░ »
   q_3: ┤3                                                                 ├─░─»
        └──────────────────────────────────────────────────────────────────┘ ░ »
meas: 4/═══════════════════════════════════════════════════════════════════════»
                                                                               »
«        ┌─┐         
«   q_0: ┤M├─────────
«        └╥┘┌─┐      
«   q_1: ─╫─┤M├──────
«         ║ └╥┘┌─┐   
«   q_2: ─╫──╫─┤M├───
«         ║  ║ └╥┘┌─┐
«   q_3: ─╫──╫──╫─┤M├
«         ║  ║  ║ └╥┘
«meas: 4/═╩══╩══╩══╩═
«         0  1  2  3 
```

## Classical baseline (greedy)
The baseline ranks assets by expected_return / risk_weight and selects the top three.

Selected assets: MSFT, GOOG, AWS

Baseline expected return score (sum): 0.3100

## Runtime comparison
Average quantum simulated runtime: 3.075 ms
Average classical baseline runtime: 0.007 ms
