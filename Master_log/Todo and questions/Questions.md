	

- What now, ElGamal gives us problems
- Should we use some Ring based scheme or other FHE scheme?
- Should we extend our system to elect more then one winner?

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




