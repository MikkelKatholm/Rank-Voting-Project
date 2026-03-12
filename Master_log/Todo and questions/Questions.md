

### Stuff to add
1. Threshold ElGamal via Verifiable Mix-Nets
	1. Encrypt a ballot using ElGamal and send it to all the servers using a mix network such that the servers does not know where it comes from
	2. **Problems?** 
		1. Can we mix it good enough?
		2. Can we just decrypt every ballot then?
2. End-to-End (E2E) Verifiability for RCV
	1. Use Bulletin Board to proof it?
3. Fully Homomorphic Encryption
	1. Use FHE to encrypt the ballots, use our circuit math to compute a round result, decrypt that round result and eliminate in the clear.
4. Sub-Quadratic Ballot Representation
	1. Can it be done?



## Whats next
Look at mixed nets 
- How do they work
- integrate into elections
Proofs for MPC

Find real world RCV elections for multiple winners



## 2026-03-04
- Look at Table of content
- How do we site out 10 ECTS report
	- Put in appendix?
	- Mark with a $\star$ ?
* It is worth the trouble to implement Networked mix nets using TLS?
* We wrote something
* **Make a clear plan for next time**
* Verifiability for SPDZ
	* It looks like we need to change the offline phase. But we don't know if that can be done without change the MP-SPDZ source code






* use electotial scheme
* Cast as intended (individual ver)
* Counted as case (universal ver)
* For old report use a normal citation with a github like


- Make verifaible shuffel code and text work
- Make the code
- Understnd the paper (Mix nets verfiability)
- _Send diego papaers (SPDZ verifiability)_
- Add a SPDZ verafibility protcol to the thesis no matter if we implement it
- Add stuff from the old report to the thesis. and cite it.






# 2026-03-18
- Adding an appendix section with terms like RCV STV, Instant-run-off, Proportinal-RCV, ...
- Proving non interactive ZKP, Fiat-Shamir. Some default way to do it???