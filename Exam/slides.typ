#import "@preview/slydst:0.1.5": *

#show: slides.with(
  title: "Eliminating Candidates, Not Privacy",
  subtitle: "Secure Ranked Choice Voting Using MPC",
  date: none,
  authors: ("Mikkel Katholm (& Emil Mors)"),
  layout: "medium",
  ratio: 16/9,
  title-color: none,
  subslide-numbering: none,
)

= Voting Systems
== Plurality Voting
- Each voter selects one candidate.
- The candidate with the most votes wins.

=== Advantages
- Simple and easy to understand.
- Quick to count and determine the winner.

=== Disadvantages
- *Strategic Voting:* Voters may not vote for their true favorite to avoid "wasting" their vote.
- *Limited expressiveness:* Voters can only express a preference for one candidate.
- *Election of minority winners:* The winner might not have majority support.
- *Preceived wasted votes:* Votes for losing candidates do not contribute to the outcome.

== Ranked Choice Voting
+ Rank candidates.
+ Check first-choice votes for a majority winner.
+ If no majority, eliminate lowest candidate and redistribute votes.
+ Repeat until a candidate has a majority.

=== Advantages
- Reduces vote splitting.
- Removes strategic voting (NP-complete). [BTT89]
- More expressive
- Broader support for winners (Potentially).

=== Disadvantages
- More complex to understand and implement.
- Longer counting process.
- Complex decision-making for voters.

== Comparison of systems
#align(horizon)[
#show table.cell.where(y: 0): set text(weight: "bold") 
#set table(
  stroke: (x,y) => if y == 0{
    (bottom: 0.7pt + black)
  }

)
#figure(
  table(
    columns: 3,
    stroke: (x,y) => if y == 0{
      (bottom: 0.7pt + black)
    },
    table.vline(x: 1, start: 1, stroke: 0.7pt + black),
    table.vline(x: 2, start: 1, stroke: 0.7pt + black),
    table.header[Property][Plurality Voting][Ranked Choice Voting],
        [Voter Decision Complexity]   , [Lower] , [Higher] ,
        [System Complexity]           , [Lower] , [Higher] ,
        [Strategic Voting]            , [Yes]   , [No]     ,
        [Expressiveness]              , [Lower] , [Higher] ,
        [Wasted Votes]                , [More]  , [Fewer] 
  ),
  caption: [Summary of properties of Plurality Voting and Ranked Choice Voting],
) <probe-a>
]
= Prior work
== "Ranked Choice Voting" using Borda Count
- A secure verifiable ranked choice online voting system based on homomorphic encryption \ _by Xuechao Yang, Xun Yi, Surya Nepal, Andrei Kelarev, and Han Fengling_
- Secure ranked choice online voting system via intel sgx and blockchain\ _by Xuechao Yang, Xun Yi, and Andrei Kelarev_

=== Shortcomings
- Uses Borda Count instead of true Ranked Choice Voting.


= Our Contribution
== Design and Choices
- *Adversarial Servers:* A subset of servers may be malicious.
- *Honest Voters/Clients:* Voters follow the protocol correctly.
- *Network Communication:* All communication channels are secure and authenticated.
#figure(
  image("images/clients_servers.drawio.png", height: 78%)
)

== Data Representation
=== Ballots
- A $C times C$ matrix $B$ where 
$ B[i,j] = cases(
  1 "if candidate" j "is the" i"th choice",
  0 "otherwise"
) $
Example: For 3 candidates and a voter prefered order [2, 0, 1]. The ballot matrix is:
$ mat(0,1,0 ;
      0,0,1 ;
      1,0,0) $ 
=== Active Candidates
- A vector $A$ of length $C$ where 
$ A[i] = cases(
  0 "if candidate" i "is eliminated",
  1 "otherwise"
) $



== The Circuit
#figure(
  image("images/Circuit.png")
)

== Protocol Overview
=== Remove Eliminated Candidates
$ B_(a c t i v e) [i, j] = B [i, j] dot.op A [i] $

=== Remove Non-highest Candidates
$ B_(h i g h e s t) [i, j] = B_(a c t i v e) [i, j] dot.op (product_k^(i - 1) (1 - sum_j B_(a c t i v e) [k, j])) $

=== Sum All Rows
$ v [j] = sum_(i in [1, C]) B_(h i g h e s t) [i, j] $

=== Sum Vectors
$ V [j] = sum_(i = 1)^C v_i [j] $

== Leakage Model
=== Minimal Leakage
- Only the winning candidate ID is leaked.
- Candidate to eliminate are computed using secure multiparty computation. (non-trivial gate)

=== Round based Leakage
- After each round, the full vector of vote counts is leaked. That is $V$.
- Findind the candidate to eliminate is trivial, and not done using MPC

= Experimental Results\ #text("(Pretty Pictures)", size: 14pt)

== Varying Number of Servers
#figure(
  image("images/vary_servers_all.png"),
  caption: [Run time of an election with 3 candidates and 32 voters, varying the number of servers],  
)

== Varying Number of Voters
#figure(
  image("images/vary_voters_all.png"),
  caption: [Run time of an election with 3 candidates and varying number of voters, using 3 servers],  
)

== Varying Number of Candidates
#figure(
  image("images/vary_candidates_all.png"),
  caption: [Run time of an election with 32 voters and varying number of candidates, using 3 servers],  
)

== Candidates scaling
#figure(
  image("images/candidates_squared.png"),
  caption: [Runtime scaling with number of candidates, showing quadratic]
)

= Questions?