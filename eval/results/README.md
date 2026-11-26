# Model Evaluation: Metrics and Complete Answers

> Generated from the repository's saved evaluation JSON. This document does not rerun models or alter scores.

## Executive verdict

The new fine-tuned 3B adapter is the strongest tested **evidence-conditioned answer model**. On 100 held-out examples, mean token F1 increased from **0.2281** to **0.8747**, normalized exact matches increased from **1/100** to **74/100**, and correct insufficient-evidence refusals increased from **2/11** to **10/11**.

On the separate 50-question system benchmark, the 120B cloud model scored **39/50 (78%)**, the original 3B+KG system scored **37/50 (74%)**, and raw 3B scored **27/50 (54%)**. The fine-tuned 3B+KG combination has not yet been rerun on that benchmark and therefore has no directly comparable 50-question score.

## Configuration ranking

1. **Fine-tuned 3B + KG — provisional production choice.** Expected to combine improved synthesis with retrieval, but the combined 50-question result is still pending.
2. **120B cloud — strongest measured general baseline.** 39/50 overall and 26/30 on public questions.
3. **Original 3B + KG — strongest measured graph-specific configuration.** 20/20 on graph-specific questions, though strict grounded correctness was 17/50.
4. **Fine-tuned 3B alone — strongest measured evidence-conditioned local model.** 0.8747 mean token F1 on the held-out v2 sample.
5. **Raw 3B — weakest configuration.** 27/50 on the system benchmark and 0.2281 token F1 on the held-out adapter comparison.

## 50-question system benchmark

| Configuration | Correct | Accuracy | Public | Profile-specific | KG facts |
|---|---:|---:|---:|---:|---:|
| Raw 3B | 27/50 | 54.0% | 19/30 | 1/8 | 7/12 |
| Original 3B + KG | 37/50 | 74.0% | 17/30 | 8/8 | 12/12 |
| 120B cloud | 39/50 | 78.0% | 26/30 | 3/8 | 10/12 |

- Strict grounded correctness for original 3B+KG: **17/50 (34.0%)**
- Retrieval recall@k: **70.0%**
- Valid citation rate: **36.0%**
- Cloud model: `openai/gpt-oss-120b`

## 100-example held-out adapter comparison

| Metric | Raw 3B | Fine-tuned 3B |
|---|---:|---:|
| Mean token F1 | 0.2281 | **0.8747** |
| Refusal recall | 18.2% | **90.9%** |
| Citation identifier validity | 100.0% | 100.0% |
| Raw-triplet-free rate | 100.0% | 100.0% |
| Normalized exact matches | 1/100 | **74/100** |
| Citation presence | 0/100 | **87/100** |

### Category-level mean token F1

| Category | Examples | Raw 3B | Fine-tuned 3B |
|---|---:|---:|---:|
| Extractive answer | 36 | 0.3004 | **0.8307** |
| Grounded QA | 28 | 0.2123 | **0.9071** |
| Multi-hop | 25 | 0.1662 | **0.8866** |
| Unanswerable | 11 | 0.1722 | **0.9091** |

The paired mean-F1 improvement is **+0.6466** with a bootstrap 95% interval of **+0.5849 to +0.7047** on this 100-example sample.

## Complete 50-question answers

Each entry shows the saved expected concepts and the exact outputs from all three configurations.

<details>
<summary><strong>Q1. Who invented the Python programming language?</strong> — public</summary>

**Expected concepts:** GuidoVanRossum

**Raw 3B — PASS**

    Guido van Rossum created the Python programming language in 1989.

**Original 3B + KG — FAIL**

    The question "Who invented the Python programming language?" cannot be answered based solely on the provided evidence. The evidence does not mention anyone inventing Python; it primarily discusses various programming languages and their characteristics. Therefore, the answer is that the evidence does not provide information about who invented Python.

**120B cloud — PASS**

    Python was created by Guido van Rossum, who first released it in 1991.

**Retrieval:** route `local`, confidence `0.694`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q2. Who invented JavaScript?</strong> — public</summary>

**Expected concepts:** BrendanEich

**Raw 3B — PASS**

    Brendan Eich created JavaScript while working at Netscape Communications Corporation in 1995.

**Original 3B + KG — PASS**

    Brendan Eich invented JavaScript.

**120B cloud — PASS**

    JavaScript was invented by Brendan Eich in 1995 while he was working at Netscape.

**Retrieval:** route `local`, confidence `0.714`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q3. Who developed TypeScript?</strong> — public</summary>

**Expected concepts:** AndersHejlsberg

**Raw 3B — FAIL**

    TypeScript was developed by Microsoft as an open-source programming language that adds static typing to JavaScript, enhancing its capabilities for large-scale applications.

**Original 3B + KG — PASS**

    Anders Hejlsberg developed TypeScript.

**120B cloud — PASS**

    TypeScript was developed by Microsoft, primarily authored by Anders Hejlsberg.

**Retrieval:** route `local`, confidence `0.668`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q4. Who developed the Java programming language?</strong> — public</summary>

**Expected concepts:** JamesGosling

**Raw 3B — PASS**

    James Gosling developed the Java programming language.

**Original 3B + KG — FAIL**

    Niklaus Wirth developed Pascal Language.

**120B cloud — PASS**

    The Java programming language was developed by James Gosling and his team at Sun Microsystems.

**Retrieval:** route `local`, confidence `0.687`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q5. Who invented C++?</strong> — public</summary>

**Expected concepts:** BjarneStroustrup

**Raw 3B — PASS**

    Bjarne Stroustrup developed C++.

**Original 3B + KG — PASS**

    Bjarne Stroustrup invented C++. [F2]

**120B cloud — PASS**

    C++ was invented by Bjarne Stroustrup in the early 1980s.

**Retrieval:** route `local`, confidence `0.66`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q6. Who invented the Rust programming language?</strong> — public</summary>

**Expected concepts:** GraydonHoare

**Raw 3B — PASS**

    Graydon Hoare invented the Rust programming language.

**Original 3B + KG — FAIL**

    The evidence provided does not mention anyone inventing the Rust programming language. Therefore, I cannot answer this question based on the given information.

**120B cloud — PASS**

    The Rust programming language was invented by Graydon Hoare while working at Mozilla.

**Retrieval:** route `local`, confidence `0.691`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q7. Who developed the Swift programming language?</strong> — public</summary>

**Expected concepts:** ChrisLattner

**Raw 3B — FAIL**

    Apple Inc. developed the Swift programming language.

**Original 3B + KG — FAIL**

    Swift was developed by Apple Inc.

**120B cloud — PASS**

    Swift was developed by Apple, led by Chris Lattner and his team.

**Retrieval:** route `local`, confidence `0.696`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q8. Who invented the Ruby programming language?</strong> — public</summary>

**Expected concepts:** YukihiroMatsumoto

**Raw 3B — PASS**

    Yukihiro Matsumoto created Ruby in 1995 as a dynamic, object-oriented scripting language influenced by Perl, Smalltalk, Lisp, and C.

**Original 3B + KG — FAIL**

    The evidence provided does not mention any individual who invented the Ruby programming language. Therefore, there is no information available to answer this question based on the given data.

**120B cloud — PASS**

    Yukihiro “Matz” Matsumoto invented the Ruby programming language.

**Retrieval:** route `local`, confidence `0.684`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q9. Who developed the Scala programming language?</strong> — public</summary>

**Expected concepts:** MartinOdersky

**Raw 3B — PASS**

    Martin Odersky developed the Scala programming language.

**Original 3B + KG — PASS**

    Martin Odersky developed the Scala programming language. [F12]

**120B cloud — PASS**

    Scala was developed by Martin Odersky and his team at the École Polytechnique Fédérale de Lausanne (EPFL).

**Retrieval:** route `local`, confidence `0.696`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q10. Who developed the Perl programming language?</strong> — public</summary>

**Expected concepts:** LarryWall

**Raw 3B — PASS**

    Larry Wall created Perl, a high-level programming language designed for text processing and web applications.

**Original 3B + KG — FAIL**

    The evidence does not provide information about who developed the Perl programming language. The question cannot be answered based on the given facts.

**120B cloud — PASS**

    Larry Wall developed the Perl programming language.

**Retrieval:** route `local`, confidence `0.682`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q11. Who invented the Lua programming language?</strong> — public</summary>

**Expected concepts:** RobertoIerusalimschy

**Raw 3B — FAIL**

    Brendan Eich created Lua, a lightweight scripting language designed for embedded systems and rapid application development.

**Original 3B + KG — PASS**

    Roberto Ierusalimschy invented the Lua programming language. [F8]

**120B cloud — PASS**

    Lua was invented by Roberto Ierusalimschy, Luiz Henrique de Figueiredo, and Waldemar Celes at Brazil’s Pontifical Catholic University of Rio de Janeiro.

**Retrieval:** route `local`, confidence `0.701`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q12. Who developed the Julia programming language?</strong> — public</summary>

**Expected concepts:** JeffBezanson

**Raw 3B — PASS**

    Julia was developed by Jeff Bezanson, Alan Edelman, Stefan Karpinski, and Viral Shah.

**Original 3B + KG — FAIL**

    The evidence provided does not mention any specific individual who developed the Julia programming language. Therefore, I cannot provide an answer based on the given information.

**120B cloud — PASS**

    The Julia programming language was developed by a team of researchers including Jeff Bezanson, Stefan Karpinski, Viral B. Shah, and Alan Edelman.

**Retrieval:** route `local`, confidence `0.682`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q13. Who developed the Fortran programming language?</strong> — public</summary>

**Expected concepts:** JohnBackus

**Raw 3B — PASS**

    John Backus developed the Fortran programming language.

**Original 3B + KG — PASS**

    John Backus developed the Fortran programming language. [F3]

**120B cloud — PASS**

    Fortran was developed by a team at IBM led by John Backus in the 1950s.

**Retrieval:** route `local`, confidence `0.701`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q14. Who invented Pascal?</strong> — public</summary>

**Expected concepts:** NiklausWirth

**Raw 3B — FAIL**

    Blaise Pascal, a French mathematician, physicist, and philosopher, is credited with inventing the first mechanical calculator called the Pascaline around 1642.

**Original 3B + KG — PASS**

    Niklaus Wirth invented Pascal.

**120B cloud — FAIL**

    Pascal was invented by the Swiss mathematician and philosopher Blaise Pascal in the 17th century.

**Retrieval:** route `local`, confidence `0.668`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q15. Who developed Prolog?</strong> — public</summary>

**Expected concepts:** AlainColmerauer

**Raw 3B — PASS**

    Prolog was developed by Alain Colmerauer at the University of Paris in 1972.

**Original 3B + KG — PASS**

    Robert Bernecky and Alain Colmerauer developed Prolog.

**120B cloud — PASS**

    Prolog was developed by Alain Colmerauer and his team at the University of Marseille in the early 1970s.

**Retrieval:** route `local`, confidence `0.665`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q16. Who invented Lisp?</strong> — public</summary>

**Expected concepts:** JohnMcCarthy

**Raw 3B — PASS**

    John McCarthy invented Lisp, a programming language developed at MIT in the 1950s.

**Original 3B + KG — PASS**

    John McCarthy invented Lisp.

**120B cloud — PASS**

    Lisp was invented by John McCarthy in 1958 while he was a professor at the Massachusetts Institute of Technology (MIT).

**Retrieval:** route `local`, confidence `0.665`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q17. Who developed Clojure?</strong> — public</summary>

**Expected concepts:** RichHickey

**Raw 3B — PASS**

    Rich Hickey developed Clojure.

**Original 3B + KG — FAIL**

    Martin Odersky developed Scala, which influenced Clojure.

**120B cloud — PASS**

    Clojure was developed by Rich Hickey.

**Retrieval:** route `local`, confidence `0.694`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q18. Who developed the F# programming language?</strong> — public</summary>

**Expected concepts:** DonSyme

**Raw 3B — FAIL**

    The F# programming language was developed by Microsoft Research.

**Original 3B + KG — PASS**

    Don Syme developed the F# programming language. [F9]

**120B cloud — PASS**

    F# was developed by Microsoft Research, primarily led by Don Syme.

**Retrieval:** route `local`, confidence `0.696`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q19. Who developed OCaml?</strong> — public</summary>

**Expected concepts:** XavierLeroy

**Raw 3B — PASS**

    OCaml was developed by Xavier Leroy at INRIA, France.

**Original 3B + KG — FAIL**

    OCaml was developed by INRIA.

**120B cloud — FAIL**

    OCaml was developed by the Caml research team at INRIA (the French Institute for Research in Computer Science and Automation).

**Retrieval:** route `local`, confidence `0.665`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q20. Who developed the Bash shell?</strong> — public</summary>

**Expected concepts:** BrianFox

**Raw 3B — FAIL**

    Bash was developed by Brian Kernighan and Dennis Ritchie at Bell Labs in 1973.

**Original 3B + KG — PASS**

    Brian Fox developed the Bash shell.

**120B cloud — PASS**

    The Bash shell was developed by Brian Fox for the GNU Project in 1989.

**Retrieval:** route `local`, confidence `0.658`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q21. Who developed the Awk programming language?</strong> — public</summary>

**Expected concepts:** AlfredAho | PeterWeinberger | BrianKernighan

**Raw 3B — FAIL**

    The Awk programming language was developed by Brian Kernighan and Dennis Ritchie at Bell Labs in 1976.

**Original 3B + KG — FAIL**

    Peter Weibergner developed the Awk programming language.

**120B cloud — PASS**

    Awk was developed by Alfred Aho, Peter Weinberger, and Brian Kernighan at Bell Labs.

**Retrieval:** route `local`, confidence `0.699`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q22. Who developed Sed?</strong> — public</summary>

**Expected concepts:** LeeMcMahon

**Raw 3B — FAIL**

    Sed was developed by Bill Joy at Sun Microsystems in 1973.

**Original 3B + KG — FAIL**

    Ken Thompson developed Sed.

**120B cloud — PASS**

    Sed was developed by Lee E. McMahon at Bell Labs.

**Retrieval:** route `local`, confidence `0.668`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q23. Who developed Matlab?</strong> — public</summary>

**Expected concepts:** CleveMoler

**Raw 3B — FAIL**

    MathWorks developed MATLAB.

**Original 3B + KG — PASS**

    Cleve Moler developed MATLAB. [F2]

**120B cloud — PASS**

    MATLAB was developed by Cleve Moler and his team at the University of New Mexico, later commercialized by the company MathWorks.

**Retrieval:** route `local`, confidence `0.661`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q24. Who developed the Scheme programming language?</strong> — public</summary>

**Expected concepts:** GeraldJaySussman

**Raw 3B — PASS**

    The Scheme programming language was developed by Guy Lewis Steele Jr. and Gerald Jay Sussman at MIT's AI Lab in the 1970s.

**Original 3B + KG — PASS**

    Guy L Steele Jr and Gerald Jay Sussman developed the Scheme programming language.

**120B cloud — PASS**

    Scheme was developed at MIT in the 1970s by Guy L. Steele and Gerald Jay Sussman.

**Retrieval:** route `local`, confidence `0.701`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q25. Who developed the BubbleSort algorithm?</strong> — public</summary>

**Expected concepts:** EdwardHarryFriendJr

**Raw 3B — FAIL**

    The BubbleSort algorithm was developed by Tony Hoare in 1956.

**Original 3B + KG — FAIL**

    BubbleSort was not developed by any of the individuals or entities mentioned in the provided evidence. The evidence focuses on MergeSort and RadixSort, but does not mention BubbleSort at all. Therefore, there is no information available to answer this question based solely on the given data.

**120B cloud — FAIL**

    Bubble Sort was first described by computer scientist John von Neumann in 1956.

**Retrieval:** route `local`, confidence `0.727`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q26. Who developed the MergeSort algorithm?</strong> — public</summary>

**Expected concepts:** JohnVonNeumann

**Raw 3B — PASS**

    MergeSort was developed by John von Neumann in 1945.

**Original 3B + KG — FAIL**

    John Wiley developed the MergeSort algorithm.

**120B cloud — PASS**

    Merge sort was developed by John von Neumann in 1945.

**Retrieval:** route `local`, confidence `0.665`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q27. Who developed QuickSort?</strong> — public</summary>

**Expected concepts:** TonyHoare

**Raw 3B — PASS**

    QuickSort was developed by Tony Hoare in 1959.

**Original 3B + KG — PASS**

    QuickSort was developed by Tony Hoare.

**120B cloud — PASS**

    QuickSort was developed by British computer scientist Tony Hoare in 1960.

**Retrieval:** route `local`, confidence `0.665`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q28. Who developed TimSort?</strong> — public</summary>

**Expected concepts:** TimPeters

**Raw 3B — FAIL**

    TimSort was developed by Python's creator, Guido van Rossum.

**Original 3B + KG — PASS**

    TimSort was developed by Tim Peters.

**120B cloud — PASS**

    TimSort was developed by Tim Peters in 2002.

**Retrieval:** route `local`, confidence `0.701`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q29. What problem does Dijkstra's algorithm solve?</strong> — public</summary>

**Expected concepts:** ShortestPathProblem

**Raw 3B — PASS**

    Dijkstra's algorithm solves the single-source shortest path problem, finding the shortest path from a source node to all other nodes in a weighted graph.

**Original 3B + KG — PASS**

    Dijkstra's algorithm solves the ShortestPathProblem.

**120B cloud — FAIL**

    Dijkstra's algorithm finds the shortest‑path distances from a single source vertex to all other vertices in a weighted graph with non‑negative edge weights.

**Retrieval:** route `local`, confidence `0.692`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q30. What problem does the Edmonds-Karp algorithm solve?</strong> — public</summary>

**Expected concepts:** MaximumFlowProblem

**Raw 3B — PASS**

    The Edmonds-Karp algorithm solves the maximum flow problem by finding the shortest augmenting path between source and sink nodes in a network, repeatedly updating the flow until no more augmenting paths exist.

**Original 3B + KG — PASS**

    The Edmonds-Karp algorithm solves the Maximum Flow Problem.

**120B cloud — PASS**

    The Edmonds‑Karp algorithm solves the maximum‑flow problem by finding the greatest possible flow from a source to a sink in a capacitated network.

**Retrieval:** route `local`, confidence `0.694`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q31. What academic position does Prasanna Kumar hold?</strong> — kg-private</summary>

**Expected concepts:** AssociateProfessor

**Raw 3B — FAIL**

    Prasanna Kumar holds the position of Professor at the Indian Institute of Technology, Madras.

**Original 3B + KG — PASS**

    Prasanna Kumar holds the position of Associate Professor.

**120B cloud — PASS**

    Prasanna Kumar is an Associate Professor in the Department of Computer Science and Engineering at the Indian Institute of Technology Delhi.

**Retrieval:** route `local`, confidence `0.701`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q32. Which courses does Prasanna Kumar teach?</strong> — kg-private</summary>

**Expected concepts:** DataStructures | Algorithms

**Raw 3B — PASS**

    Prasanna Kumar teaches Computer Science, Data Structures, Algorithms, and Machine Learning at the University of California, Berkeley.

**Original 3B + KG — PASS**

    Prasanna Kumar teaches courses Algorithms and Data Structures.

**120B cloud — FAIL**

    I’m sorry, but I don’t have information on the courses taught by Prasanna Kumar.

**Retrieval:** route `local`, confidence `0.701`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q33. Whom does Prasanna Kumar supervise?</strong> — kg-private</summary>

**Expected concepts:** PhDStudents

**Raw 3B — FAIL**

    Prasanna Kumar supervises the Chief Executive Officer (CEO) of a multinational corporation.

**Original 3B + KG — PASS**

    Prasanna Kumar supervises PhD students.

**120B cloud — PASS**

    Prasanna Kumar supervises his graduate (PhD/Master’s) students.

**Retrieval:** route `local`, confidence `0.668`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q34. What are Prasanna Kumar's research interests?</strong> — kg-private</summary>

**Expected concepts:** MachineLearning | DistributedSystems

**Raw 3B — FAIL**

    Prasanna Kumar's research interests include machine learning, computer vision, and natural language processing.

**Original 3B + KG — PASS**

    Prasanna Kumar's research interests include Machine Learning and Distributed Systems.

**120B cloud — FAIL**

    Prasanna Kumar’s research interests focus on algorithm design and analysis, particularly in graph algorithms, combinatorial optimization, and their applications to network science and data mining.

**Retrieval:** route `local`, confidence `0.699`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q35. What paper did Prasanna Kumar publish?</strong> — kg-private</summary>

**Expected concepts:** DeepLearningForIoT

**Raw 3B — FAIL**

    Prasanna Kumar published "A New Approach to the Study of Indian History."

**Original 3B + KG — PASS**

    Prasanna Kumar published the paper "DeepLearningForIoT". [F8]

**120B cloud — FAIL**

    Prasanna Kumar published the paper titled “A Study on the Performance of the Hybrid Genetic Algorithm for Solving the Traveling Salesman Problem.”

**Retrieval:** route `local`, confidence `0.663`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q36. What award did Prasanna Kumar receive?</strong> — kg-private</summary>

**Expected concepts:** BestTeacherAward2022

**Raw 3B — FAIL**

    Prasanna Kumar received the Padma Shri, India's fourth-highest civilian honor, for his contributions to science and technology.

**Original 3B + KG — PASS**

    Prasanna Kumar received the Best Teacher Award 2022. [F7]

**120B cloud — FAIL**

    Prasanna Kumar was honored with the Shanti Swarup Bhatnagar Prize for Science and Technology.

**Retrieval:** route `local`, confidence `0.694`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q37. Where does Prasanna Kumar reside?</strong> — kg-private</summary>

**Expected concepts:** Chennai

**Raw 3B — FAIL**

    Prasanna Kumar resides in Bangalore, Karnataka, India.

**Original 3B + KG — PASS**

    Prasanna Kumar resides in Chennai. [F7]

**120B cloud — FAIL**

    I’m sorry, but I don’t have any publicly available information about Prasanna Kumar’s place of residence.

**Retrieval:** route `local`, confidence `0.661`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q38. Which professional organizations is Prasanna Kumar a member of?</strong> — kg-private</summary>

**Expected concepts:** IEEE | ACM

**Raw 3B — FAIL**

    Prasanna Kumar is a member of the Indian Institute of Management (IIM) Ahmedabad, the National Academy of Engineering (NAE), and the American Society for Mechanical Engineers (ASME).

**Original 3B + KG — PASS**

    Prasanna Kumar is a member of ACM and IEEE.

**120B cloud — PASS**

    Prasanna Kumar is a member of the IEEE, the ACM, and the SPIE professional societies.

**Retrieval:** route `local`, confidence `0.658`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q39. Which languages did Pascal influence?</strong> — kg-fact</summary>

**Expected concepts:** Modula2 | Ada

**Raw 3B — FAIL**

    Pascal influenced the development of several programming languages, including C, Java, and Fortran.

**Original 3B + KG — PASS**

    Pascal influenced Ada, Modula-2, and JavaScript.

**120B cloud — PASS**

    Pascal influenced several languages, notably Algol 60, Modula‑2, Ada, Oberon, and later educational and teaching languages such as Delphi/Object Pascal, as well as contributing concepts to C, Java, and many modern structured and object‑oriented languages.

**Retrieval:** route `local`, confidence `0.699`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q40. Which company developed Turbo Pascal?</strong> — kg-fact</summary>

**Expected concepts:** Borland

**Raw 3B — PASS**

    Turbo Pascal was developed by Borland International.

**Original 3B + KG — PASS**

    TurboPascal was developed by Borland. This can be inferred from [F2], which states that TurboPascal was developed by Borland.

**120B cloud — PASS**

    Turbo Pascal was developed by Borland.

**Retrieval:** route `local`, confidence `0.665`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q41. Which two core mechanisms does Prolog support?</strong> — kg-fact</summary>

**Expected concepts:** Backtracking | Unification

**Raw 3B — PASS**

    Prolog supports backtracking and unification as its core mechanisms.

**Original 3B + KG — PASS**

    Prolog supports Unification and Backtracking.

**120B cloud — PASS**

    Prolog’s core mechanisms are unification (pattern matching of terms) and backtracking (systematic search through alternative solutions).

**Retrieval:** route `local`, confidence `0.699`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q42. Name two areas where OCaml is used.</strong> — kg-fact</summary>

**Expected concepts:** CompilerConstruction | FormalVerification

**Raw 3B — FAIL**

    OCaml is primarily used for developing web applications, particularly those requiring high performance and scalability. It is also widely used in scientific computing and data analysis due to its strong type system and efficient execution.

**Original 3B + KG — PASS**

    OCaml is used in compiler construction and formal verification. [F7], [F14]

**120B cloud — FAIL**

    OCaml is widely used in formal verification (e.g., the Coq proof assistant) and in financial technology for building high‑performance trading and risk‑analysis systems.

**Retrieval:** route `local`, confidence `0.66`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q43. Which simulation product is included in MATLAB?</strong> — kg-fact</summary>

**Expected concepts:** Simulink

**Raw 3B — PASS**

    Simulink is a simulation product included in MATLAB.

**Original 3B + KG — PASS**

    Simulink is included in MATLAB. This can be inferred from [F2], which states that MATLAB includes Simulink.

**120B cloud — PASS**

    MATLAB includes the Simulink simulation product for modeling, simulating, and analyzing dynamic systems.

**Retrieval:** route `local`, confidence `0.676`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q44. Which partitioning technique does Quicksort use?</strong> — kg-fact</summary>

**Expected concepts:** Partitioning

**Raw 3B — PASS**

    Quicksort uses the Lomuto partitioning scheme, which selects a pivot element and partitions the array around it to sort elements less than and greater than the pivot.

**Original 3B + KG — PASS**

    Quicksort uses Partitioning as a technique to divide the array into sub-arrays based on a pivot element. This is supported by [F1], [F2], and [F3].

**120B cloud — PASS**

    Quicksort uses **divide‑and‑conquer partitioning**, repeatedly splitting the array into elements less than a chosen pivot and elements greater than the pivot.

**Retrieval:** route `local`, confidence `0.701`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q45. Is Quicksort a stable sorting algorithm?</strong> — kg-fact</summary>

**Expected concepts:** notstable

**Raw 3B — PASS**

    No, Quicksort is not a stable sorting algorithm.

**Original 3B + KG — PASS**

    No, Quicksort is not a stable sorting algorithm. This can be determined from fact [F5], which states that Quicksort is stable False.

**120B cloud — PASS**

    No; Quicksort is not a stable sorting algorithm unless specifically modified to preserve the relative order of equal elements.

**Retrieval:** route `local`, confidence `0.665`, expected evidence found `False`.

</details>

<details>
<summary><strong>Q46. Name two areas where Lua is used.</strong> — kg-fact</summary>

**Expected concepts:** GameDevelopment | EmbeddedSystems

**Raw 3B — FAIL**

    Lua is primarily used for game scripting, particularly in the development of video games, and as a server-side language for web applications.

**Original 3B + KG — PASS**

    Lua is used in game development and embedded systems.

**120B cloud — PASS**

    Lua is commonly used in game development (e.g., scripting game logic) and embedded systems for configuration or automation tasks.

**Retrieval:** route `local`, confidence `0.656`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q47. What does clean cooking reduce?</strong> — kg-fact</summary>

**Expected concepts:** IndoorAirPollution

**Raw 3B — FAIL**

    Clean cooking reduces the risk of foodborne illnesses by minimizing exposure to harmful bacteria, chemicals, and pollutants during the preparation process.

**Original 3B + KG — PASS**

    Clean cooking reduces Indoor Air Pollution [F1].

**120B cloud — PASS**

    Clean cooking reduces indoor air pollution, greenhouse‑gas emissions, and associated health risks.

**Retrieval:** route `expand`, confidence `0.468`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q48. What does water sanitation improve?</strong> — kg-fact</summary>

**Expected concepts:** PublicHealth

**Raw 3B — PASS**

    Water sanitation improves public health by reducing the spread of diseases through contaminated water sources.

**Original 3B + KG — PASS**

    WaterSanitation improves PublicHealth [F1].

**120B cloud — PASS**

    Water sanitation improves public health by reducing disease transmission, preventing water‑borne illnesses, and promoting safer drinking water and hygiene.

**Retrieval:** route `local`, confidence `0.735`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q49. What does rural electrification improve?</strong> — kg-fact</summary>

**Expected concepts:** EducationOutcomes

**Raw 3B — FAIL**

    Rural electrification improves access to electricity, reducing energy poverty, improving health outcomes, enhancing agricultural productivity, and fostering economic development.

**Original 3B + KG — PASS**

    Rural Electrification improves Education Outcomes [F1].

**120B cloud — FAIL**

    Rural electrification improves household living standards, economic productivity, education, healthcare services, and overall community development.

**Retrieval:** route `local`, confidence `0.735`, expected evidence found `True`.

</details>

<details>
<summary><strong>Q50. What does deforestation contribute to?</strong> — kg-fact</summary>

**Expected concepts:** ClimateChange

**Raw 3B — PASS**

    Deforestation contributes to climate change by releasing stored carbon dioxide into the atmosphere, altering local ecosystems, and reducing biodiversity.

**Original 3B + KG — PASS**

    Deforestation contributes to Climate Change [F1].

**120B cloud — PASS**

    Deforestation contributes to climate change by releasing stored carbon dioxide, loss of biodiversity, soil erosion, and disruption of water cycles.

**Retrieval:** route `expand`, confidence `0.518`, expected evidence found `True`.

</details>

## Complete 100-example raw-versus-adapter answers

These examples test answer synthesis from supplied evidence; they do not test retrieval or general world knowledge.

<details>
<summary><strong>A1. How often is Politics & Policy not published?</strong> — unanswerable</summary>

**Expected answer**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Politics & Policy is published several times a week.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A2. Masjid al-Qiblatayn, is a mosque in which city, situated in the northwestern Awdal region of Somaliland, officially the Republic of Somaliland, is a self-declared state internationally recognised as an autonomous region of Somalia?</strong> — grounded_qa</summary>

**Expected answer**

    Zeila. [F1]

**Raw 3B**

    Masjid al-Qiblatayn is located in Zeila, which is situated in the northwestern Awdal region of Somaliland. Somaliland is an internationally recognised state that is self-declared and is an autonomous region of Somalia.

**Fine-tuned 3B**

    Zeila. [F1]

</details>

<details>
<summary><strong>A3. How many people identify as gay or bisexual in NYC?</strong> — extractive_answer</summary>

**Expected answer**

    568,903. [F1]

**Raw 3B**

    According to the evidence provided, approximately 568,903 individuals in the New York metropolitan area identify as gay or bisexual. This figure represents the largest self-identifying gay and bisexual community in the United States and one of the world's largest.

**Fine-tuned 3B**

    568,903. [F1]

</details>

<details>
<summary><strong>A4. Hangman stars what actress who began her acting career in "Campfire Tales"?</strong> — multi_hop</summary>

**Expected answer**

    Amy Smart. [F1] [F2]

**Raw 3B**

    Hangman stars Amy Smart, who began her acting career in "Campfire Tales."

**Fine-tuned 3B**

    Amy Smart. [F1] [F2]

</details>

<details>
<summary><strong>A5. Who was the showrunner for the Simpsons season with the episode spoofing Cape Fear?</strong> — grounded_qa</summary>

**Expected answer**

    David Mirkin. [F1]

**Raw 3B**

    The showrunner for the Simpsons season that featured the episode "Cape Feare", which is a spoof of the 1962 film "Cape Fear", was David Mirkin.

**Fine-tuned 3B**

    David Mirkin. [F1]

</details>

<details>
<summary><strong>A6. Innovative Life: The Anthology 1984-1989, is a compilation album released in 2008 by who, which American rapper, singer-songwriter, record producer and DJ?</strong> — grounded_qa</summary>

**Expected answer**

    Arabian Prince. [F1]

**Raw 3B**

    Innovative Life: The Anthology 1984-1989 is a compilation album released in 2008 by American recording artist Arabian Prince. Kim Renard Nazel, better known by the stage name Arabian Prince, is an American rapper, singer-songwriter, record producer, and DJ.

**Fine-tuned 3B**

    Arabian Prince. [F1]

</details>

<details>
<summary><strong>A7. Which genre did Madonna started out in?</strong> — extractive_answer</summary>

**Expected answer**

    rock music. [F1]

**Raw 3B**

    Madonna started out in rock music.

**Fine-tuned 3B**

    rock. [F1]

</details>

<details>
<summary><strong>A8. Which film director is younger, Del Lord or Wang Xiaoshuai?</strong> — grounded_qa</summary>

**Expected answer**

    Del Lord. [F1]

**Raw 3B**

    Wang Xiaoshuai is younger than Del Lord. Wang Xiaoshuai was born on May 22, 1966, while Del Lord was born on October 7, 1894.

**Fine-tuned 3B**

    Wang Xiaoshuai. [F1]

</details>

<details>
<summary><strong>A9. In how many countries, was this 2-seater hatchback Microcar manufactured and marketed by this group led by Annette Winkler?</strong> — multi_hop</summary>

**Expected answer**

    46 countries. [F1] [F2]

**Raw 3B**

    The Smart Fortwo was marketed in 46 countries worldwide.

**Fine-tuned 3B**

    46. [F1] [F2]

</details>

<details>
<summary><strong>A10. Who was Joseph's father?</strong> — extractive_answer</summary>

**Expected answer**

    Jacob. [F1]

**Raw 3B**

    According to the evidence provided, Joseph's father was Jacob.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A11. Which rap duo includes a performer who starred in "Sol Goode"?</strong> — multi_hop</summary>

**Expected answer**

    The Wow. [F1] [F2]

**Raw 3B**

    The rap duo that includes a performer who starred in "Sol Goode" is The Wow. According to the evidence provided, Balthazar Getty, who starred in "Sol Goode," is a member of the rap duo The Wow.

**Fine-tuned 3B**

    The Wow. [F1] [F2]

</details>

<details>
<summary><strong>A12. What strip club-related law were the council members trying to repeat?</strong> — unanswerable</summary>

**Expected answer**

    I do not have enough verified evidence to answer.

**Raw 3B**

    The council members were trying to repeat the city's "no touch" laws at strip clubs.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A13. You're No Good: was covered in a charting version by which soul singer and pianist?</strong> — multi_hop</summary>

**Expected answer**

    Betty Everett. [F1] [F2]

**Raw 3B**

    You're No Good was covered in a charting version by Betty Everett.

**Fine-tuned 3B**

    Betty Everett. [F1] [F2]

</details>

<details>
<summary><strong>A14. What organization commented on the deal between EMC and Dell?</strong> — extractive_answer</summary>

**Expected answer**

    FBR Capital Markets. [F1]

**Raw 3B**

    The organizations that commented on the deal between EMC and Dell include:
    
    1. FBR Capital Markets
    2. Fortune
    3. The Register
    4. William Blair & Company
    
    These commenters expressed varying opinions about the deal, with some praising its potential benefits while others expressing concerns about strategic synergies and market impact.

**Fine-tuned 3B**

    Commentators. [F1]

</details>

<details>
<summary><strong>A15. Where does the American singer-songwriter, Vic Chessnutt, who features on an album of covers of Gram Parsons' songs, hail from?</strong> — grounded_qa</summary>

**Expected answer**

    Athens, Georgia. [F1]

**Raw 3B**

    Vic Chesnutt hails from Athens, Georgia.

**Fine-tuned 3B**

    Athens, Georgia. [F1]

</details>

<details>
<summary><strong>A16. What did System R avoid to change the way data was stored?</strong> — unanswerable</summary>

**Expected answer**

    I do not have enough verified evidence to answer.

**Raw 3B**

    System R avoided changing the way data was stored by keeping it in a single large "chunk" for each record.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A17. What describes the connection between the conditions of cyclic existence?</strong> — extractive_answer</summary>

**Expected answer**

    The Twelve Nidānas. [F1]

**Raw 3B**

    The Twelve Nidānas describe a causal connection between the subsequent conditions or characteristics of cyclic existence, each one giving rise to the next.

**Fine-tuned 3B**

    The Twelve Nidānas. [F1]

</details>

<details>
<summary><strong>A18. How many Americans were found to have intermediate health literacy?</strong> — extractive_answer</summary>

**Expected answer**

    44%. [F1]

**Raw 3B**

    According to the evidence provided, 44% of adult Americans were found to have intermediate health literacy.

**Fine-tuned 3B**

    44%. [F1]

</details>

<details>
<summary><strong>A19. What restriction does W-VHS recordings have?</strong> — extractive_answer</summary>

**Expected answer**

    analog only. [F1]

**Raw 3B**

    W-VHS recordings are analog-only.

**Fine-tuned 3B**

    analog only. [F1]

</details>

<details>
<summary><strong>A20. What military forces usually integrate air defnce as a separate arm or part of artillery?</strong> — extractive_answer</summary>

**Expected answer**

    Western and Commonwealth militaries. [F1]

**Raw 3B**

    Most Western and Commonwealth militaries integrate air defence as a separate arm or part of artillery.

**Fine-tuned 3B**

    Most Western and Commonwealth militaries. [F1]

</details>

<details>
<summary><strong>A21. How many downloads did the lead single from Over My Head get as of January 2015?</strong> — multi_hop</summary>

**Expected answer**

    4.7 million. [F1] [F2]

**Raw 3B**

    According to the evidence provided, the lead single from "Over My Head" (which was originally titled "Cable Car") received 4.7 million downloads as of January 2015.

**Fine-tuned 3B**

    4.7 million. [F1] [F2]

</details>

<details>
<summary><strong>A22. Who has the power and right to enact statutes for interstate dealings?</strong> — extractive_answer</summary>

**Expected answer**

    Congress. [F1]

**Raw 3B**

    Congress has the power and right to enact statutes for interstate dealings.

**Fine-tuned 3B**

    Congress. [F1]

</details>

<details>
<summary><strong>A23. What is an example of a brewer that owns pubs throughout Britain?</strong> — extractive_answer</summary>

**Expected answer**

    Greene King. [F1]

**Raw 3B**

    An example of a brewer that owns pubs throughout Britain is Greene King.

**Fine-tuned 3B**

    Greene King. [F1]

</details>

<details>
<summary><strong>A24. City Centre and Melbourne City Centre is near what market?</strong> — grounded_qa</summary>

**Expected answer**

    Queen Victoria Market. [F1]

**Raw 3B**

    The city centre and Melbourne City Centre is near Queen Victoria Market.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A25. Who was the first Archivist at the National Archives?</strong> — extractive_answer</summary>

**Expected answer**

    R.D.W. Connor. [F1]

**Raw 3B**

    The first Archivist at the National Archives was R.D.W. Connor. He began serving in 1934 when the National Archives was established by Congress.

**Fine-tuned 3B**

    R.D.W. Connor. [F1]

</details>

<details>
<summary><strong>A26. The Sinfonia Varsovia is an orchestra based in Warsaw, Poland, since 2003 the orchestra has been led by which Polish composer and conductor, as its artistic director?</strong> — multi_hop</summary>

**Expected answer**

    Krzysztof Eugeniusz Penderecki. [F1] [F2]

**Raw 3B**

    The Sinfonia Varsovia is an orchestra based in Warsaw, Poland, since 2003. It has been led by Krzysztof Penderecki as its artistic director.

**Fine-tuned 3B**

    Krzysztof Eugeniusz Penderecki. [F1] [F2]

</details>

<details>
<summary><strong>A27. What border does I-19 come close to?</strong> — extractive_answer</summary>

**Expected answer**

    U.S.-Mexico border. [F1]

**Raw 3B**

    I-19 comes close to the U.S.-Mexico border.

**Fine-tuned 3B**

    U.S.-Mexico border. [F1]

</details>

<details>
<summary><strong>A28. Johannes Vermeer's works include which painting, located in the Rijksmuseum in Amsterdam, Netherlands?</strong> — multi_hop</summary>

**Expected answer**

    Vermeer works (including "The Milkmaid". [F1] [F2]

**Raw 3B**

    Johannes Vermeer's work "The Milkmaid" is located in the Rijksmuseum in Amsterdam, Netherlands.

**Fine-tuned 3B**

    The Milkmaid. [F1] [F2]

</details>

<details>
<summary><strong>A29. What drug is the main ingredient referenced in the "drank" of the song Drank in My Cup?</strong> — grounded_qa</summary>

**Expected answer**

    cough syrup. [F1]

**Raw 3B**

    The main ingredient referenced in the "drank" of the song "Drank in My Cup" is purple drank. Purple drank is a slang term for a concoction that includes prescription-strength cough syrup used in a manner inconsistent with its labeling, making it a recreational drug.

**Fine-tuned 3B**

    cough syrup. [F1]

</details>

<details>
<summary><strong>A30. What concept helps map and define people's experiences of self in society?</strong> — extractive_answer</summary>

**Expected answer**

    the concept of boundaries. [F1]

**Raw 3B**

    The concept that helps map and define people's experiences of self in society is boundaries.

**Fine-tuned 3B**

    boundaries. [F1]

</details>

<details>
<summary><strong>A31. What was the multi day of remembrance for the dead?</strong> — extractive_answer</summary>

**Expected answer**

    Parentalia. [F1]

**Raw 3B**

    The multi-day festival of remembrance for the dead was Parentalia, which took place in February.

**Fine-tuned 3B**

    Parentalia. [F1]

</details>

<details>
<summary><strong>A32. How may aircraft carriers be classified?</strong> — extractive_answer</summary>

**Expected answer**

    according to the type of aircraft they carry and their operational assignments. [F1]

**Raw 3B**

    Aircraft carriers can be classified according to the type of aircraft they carry and their operational assignments.

**Fine-tuned 3B**

    according to the type of aircraft they carry and their operational assignments. [F1]

</details>

<details>
<summary><strong>A33. May Gorslin Preston Slosson died in what Michigan county?</strong> — grounded_qa</summary>

**Expected answer**

    Washtenaw County. [F1]

**Raw 3B**

    May Gorslin Preston Slosson died in Washtenaw County, Michigan.

**Fine-tuned 3B**

    Washtenaw County. [F1]

</details>

<details>
<summary><strong>A34. The covered wagon was long the dominant form of transport in pre-industrial America, it heavily relied upon along such travel routes as the Great Wagon Road, an improved trail through which location, from Pennsylvania to North Carolina, and from there to Georgia in colonial America?</strong> — multi_hop</summary>

**Expected answer**

    Great Appalachian Valley. [F1] [F2]

**Raw 3B**

    The covered wagon was long the dominant form of transport in pre-industrial America, and it heavily relied upon along such travel routes as the Great Wagon Road, an improved trail that ran through the Great Appalachian Valley from Pennsylvania to North Carolina, and from there to Georgia in colonial America.

**Fine-tuned 3B**

    Great Appalachian Valley. [F1] [F2]

</details>

<details>
<summary><strong>A35. Angus Brayshaw is the grandson of the Australian who played what two sports?</strong> — multi_hop</summary>

**Expected answer**

    Australian rules football and cricket. [F1] [F2]

**Raw 3B**

    Angus Brayshaw is the grandson of Ian Brayshaw, who played both Australian rules football and cricket.

**Fine-tuned 3B**

    Australian rules football and cricket. [F1] [F2]

</details>

<details>
<summary><strong>A36. Who introduced a bill in 1795 about minimum wage?</strong> — extractive_answer</summary>

**Expected answer**

    Samuel Whitbread. [F1]

**Raw 3B**

    Samuel Whitbread MP introduced a bill in 1795 about minimum wage.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A37. What did Genghis Khan steal from South Asia?</strong> — unanswerable</summary>

**Expected answer**

    I do not have enough verified evidence to answer.

**Raw 3B**

    I do not have enough verified evidence to answer.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A38. Which suitcase manufacturer is named after a Peruvian artifact and has a store in an urban shopping mall in Time Warner Center in Manhattan?</strong> — multi_hop</summary>

**Expected answer**

    Tumi Holdings, Inc. [F1] [F2]

**Raw 3B**

    Based on the provided evidence, Tumi Inc. fits both criteria:
    1. It is a suitcase manufacturer named after a Peruvian artifact (Tumi is derived from the Quechua word "tumi" meaning "to carry").
    2. It has a store in an urban shopping mall in Time Warner Center in Manhattan, specifically at The Shops at Columbus Circle.
    Therefore, Tumi Inc. meets the requirements of the question.

**Fine-tuned 3B**

    Tumi. [F1] [F2]

</details>

<details>
<summary><strong>A39. During what year was the incorporated town and deep water seaport founded?</strong> — multi_hop</summary>

**Expected answer**

    1936. [F1] [F2]

**Raw 3B**

    The incorporated town and deep water seaport Searsport, Maine was founded in 1936.

**Fine-tuned 3B**

    1936. [F1] [F2]

</details>

<details>
<summary><strong>A40. Alvarezsauroidea was named after a physicist who won the Nobel Prize in Physics in what year?</strong> — grounded_qa</summary>

**Expected answer**

    1968. [F1]

**Raw 3B**

    Alvarezsauroidea was named after Luis Walter Alvarez, who won the Nobel Prize in Physics in 1968.

**Fine-tuned 3B**

    1968. [F1]

</details>

<details>
<summary><strong>A41. Did the tenants of the wealthier genrty lose their nobility?</strong> — extractive_answer</summary>

**Expected answer**

    no. [F1]

**Raw 3B**

    I do not have enough verified evidence to answer. The evidence provided states that the tenants of the wealthier gentry retained all their constitutional prerogatives, including their hereditary juridical status, which determines nobility. Therefore, it is not clear whether they lost their nobility or not based on the given information.

**Fine-tuned 3B**

    no. [F1]

</details>

<details>
<summary><strong>A42. While already serving a life sentence, Joseph Druce killed a Roman Catholic priest who had been assigned to parishes in what state?</strong> — grounded_qa</summary>

**Expected answer**

    Massachusetts. [F1]

**Raw 3B**

    While already serving a life sentence, Joseph Druce killed a Roman Catholic priest who had been assigned to parishes in Massachusetts.

**Fine-tuned 3B**

    Massachusetts. [F1]

</details>

<details>
<summary><strong>A43. What is the nationality of the designer of the set for Chronicle?</strong> — multi_hop</summary>

**Expected answer**

    Japanese American. [F1] [F2]

**Raw 3B**

    The designer of the set for Chronicle is Isamu Noguchi, who was Japanese American.

**Fine-tuned 3B**

    Japanese American. [F1] [F2]

</details>

<details>
<summary><strong>A44. Which painter created the 'Beguiling of Merlin' and was closely associated with the later part of the Pre-Raphaelite movement?</strong> — grounded_qa</summary>

**Expected answer**

    Edward Burne-Jones. [F1]

**Raw 3B**

    The painter who created the 'Beguiling of Merlin' and was closely associated with the later part of the Pre-Raphaelite movement was Edward Burne-Jones.

**Fine-tuned 3B**

    Edward Burne-Jones. [F1]

</details>

<details>
<summary><strong>A45. Which country music artist known for her song Pink Warrior has shared the stage with Miranda Lambert?</strong> — grounded_qa</summary>

**Expected answer**

    Candy Coburn. [F1]

**Raw 3B**

    Candy Coburn has shared the stage with Miranda Lambert.

**Fine-tuned 3B**

    Candy Coburn. [F1]

</details>

<details>
<summary><strong>A46. What do Witness publications say baptism symbolizes a person's personal dedication to?</strong> — extractive_answer</summary>

**Expected answer**

    God. [F1]

**Raw 3B**

    Witness publications say baptism symbolizes personal dedication to God.

**Fine-tuned 3B**

    God. [F1]

</details>

<details>
<summary><strong>A47. Over the past twenty years, rights-holders have complained to whom?</strong> — unanswerable</summary>

**Expected answer**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Over the past twenty years, rights-holders have complained to Google.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A48. Which poet is older, Robert Frost or Paul Scott?</strong> — multi_hop</summary>

**Expected answer**

    Robert Lee Frost. [F1] [F2]

**Raw 3B**

    Robert Frost is older than Paul Scott. Robert Frost was born on March 26, 1874, while Paul Scott was born on March 25, 1920.

**Fine-tuned 3B**

    Robert Lee Frost. [F1] [F2]

</details>

<details>
<summary><strong>A49. What did closer groove spacing result in?</strong> — extractive_answer</summary>

**Expected answer**

    Lower recorded volume. [F1]

**Raw 3B**

    Closer groove spacing resulted in lower recorded volume.

**Fine-tuned 3B**

    Lower recorded volume. [F1]

</details>

<details>
<summary><strong>A50. What co-writer of the Ozzy Osbourne song about the Cold War died in a plane crash in 1982?</strong> — multi_hop</summary>

**Expected answer**

    Randy Rhoads. [F1] [F2]

**Raw 3B**

    Bob Daisley died in a plane crash in 1982.

**Fine-tuned 3B**

    Randy Rhoads. [F1] [F2]

</details>

<details>
<summary><strong>A51. Where is the residence of the "Proper Education" remixer known as Cirez D?</strong> — multi_hop</summary>

**Expected answer**

    Los Angeles, California. [F1] [F2]

**Raw 3B**

    According to the evidence provided, Eric Prydz, who is known as Cirez D, resides in Los Angeles, California.

**Fine-tuned 3B**

    Los Angeles, California. [F1] [F2]

</details>

<details>
<summary><strong>A52. Where do Muslims mainly live in?</strong> — unanswerable</summary>

**Expected answer**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Muslims mainly live in rural areas of Himachal Pradesh.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A53. Which breed of dog is extinct, the Bracco Italiano or the St. John's water dog?</strong> — grounded_qa</summary>

**Expected answer**

    St. John's water dog. [F1]

**Raw 3B**

    The St. John's water dog is extinct.

**Fine-tuned 3B**

    St. John's water dog. [F1]

</details>

<details>
<summary><strong>A54. What resort has over 3,000 slot machines and is the only depiction of Soviet culture in the US?</strong> — multi_hop</summary>

**Expected answer**

    Tropicana Atlantic City. [F1] [F2]

**Raw 3B**

    Based on the provided evidence, the resort that has over 3,000 slot machines and is the only depiction of Soviet culture in the US is Mandalay Bay Resort in Las Vegas. This information can be directly inferred from the following facts:
    
    - Red Square (restaurant) is described as a Russian-themed restaurant located in the Mandalay Bay Resort in Las Vegas.
    - Red Square is noted as one of the only depictions of Soviet culture in the United States.
    - The Tropicana Casino & Resort Atlantic City, which was previously known as Red Square, had over 3,000 slot machines and 135

**Fine-tuned 3B**

    Mandalay Bay Resort. [F1] [F2]

</details>

<details>
<summary><strong>A55. The person who wrote dialogues and lyrics for the Telugu version for Sampoorna Ramayanam received the Sahitya Akademi Award in what year?</strong> — grounded_qa</summary>

**Expected answer**

    1987. [F1]

**Raw 3B**

    The person who wrote dialogues and lyrics for the Telugu version of Sampoorna Ramayanam received the Sahitya Akademi Award in 1987.

**Fine-tuned 3B**

    1987. [F1]

</details>

<details>
<summary><strong>A56. How tall is this luxury hotel and casino resort in Macau where the winners of 14th IIFA Awards were announced?</strong> — grounded_qa</summary>

**Expected answer**

    39-story. [F1]

**Raw 3B**

    The luxury hotel and casino resort in Macau where the winners of the 14th IIFA Awards were announced is The Venetian Macao. It is a 39-story building located on the Cotai Strip in Macau.

**Fine-tuned 3B**

    39-story. [F1]

</details>

<details>
<summary><strong>A57. What did Robert Kyncl confirm in May 2014?</strong> — unanswerable</summary>

**Expected answer**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Robert Kyncl confirmed that YouTube would block the content of labels who do not negotiate deals to be included in the paid service "to ensure that all content on the platform is governed by its new contractual terms."

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A58. What does the line integral of the electric field between the plates of a capacitor represent?</strong> — extractive_answer</summary>

**Expected answer**

    The voltage. [F1]

**Raw 3B**

    The line integral of the electric field between the plates of a capacitor represents the potential difference (voltage) between those plates.

**Fine-tuned 3B**

    voltage. [F1]

</details>

<details>
<summary><strong>A59. What decision allowed Gaddafi to move Libya closer to socialism?</strong> — extractive_answer</summary>

**Expected answer**

    In September 1973, it was announced that all foreign oil producers active in Libya were to be nationalized. [F1]

**Raw 3B**

    The decision that allowed Gaddafi to move Libya closer to socialism was the nationalization of the oil sector. This occurred in December 1971 when the RCC (National Command Council) began a program of nationalization, starting with the expropriation of British Petroleum's share of the British Petroleum-N.B. Hunt Sahir Field. This action marked a significant shift towards socialism and helped to boost Libya's economy and improve the standard of living for its citizens.

**Fine-tuned 3B**

    nationalization. [F1]

</details>

<details>
<summary><strong>A60. Which documentary film featured the Democrat who won a record four presidential elections?</strong> — multi_hop</summary>

**Expected answer**

    The Roosevelts: An Intimate History. [F1] [F2]

**Raw 3B**

    The documentary film that featured the Democrat who won a record four presidential elections is "The Roosevelts: An Intimate History". This film covers the lives and times of the Roosevelt family, including Franklin D. Roosevelt, who was a Democrat and won four presidential elections.

**Fine-tuned 3B**

    The Roosevelts. [F1] [F2]

</details>

<details>
<summary><strong>A61. The O'Reilly Factor for Kids writer settled how many sexual harassment lawsuits?</strong> — grounded_qa</summary>

**Expected answer**

    five. [F1]

**Raw 3B**

    The O'Reilly Factor for Kids writer, Bill O'Reilly, settled five sexual harassment lawsuits.

**Fine-tuned 3B**

    five. [F1]

</details>

<details>
<summary><strong>A62. Who wrote this 1987 Newberry Honor-winning young-adult wilderness survival novel and the fifth and final novel of that same series, called Brian's Hunt?</strong> — grounded_qa</summary>

**Expected answer**

    Gary Paulsen. [F1]

**Raw 3B**

    Gary Paulsen wrote both "Hatchet" (1987) and "Brian's Hunt" (2003).

**Fine-tuned 3B**

    Gary Paulsen. [F1]

</details>

<details>
<summary><strong>A63. The entire country was being attack and Glover believe it help people to do what?</strong> — extractive_answer</summary>

**Expected answer**

    accept and deal. [F1]

**Raw 3B**

    Glover believed that the knowledge that the entire country was being attacked and there was no way to escape the bombs helped people to accept and deal with the situation.

**Fine-tuned 3B**

    accept and deal with the situation. [F1]

</details>

<details>
<summary><strong>A64. Where does the president preside during the Chief Justice impeachment trial?</strong> — unanswerable</summary>

**Expected answer**

    I do not have enough verified evidence to answer.

**Raw 3B**

    The President presides over the impeachment trial in the Senate.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A65. The Mercedes-Benz W116, is a series of flagship luxury sedans, produced from September 1972 until 1980, the W116 automobiles were the first Mercedes-Benz models to be officially called S-Class, the Mercedes-Benz S-Class, formerly known as Sonderklasse S-Klasse, is a series of luxury flagship vehicles produced by the German automaker Mercedes-Benz, a division of which German company ?</strong> — multi_hop</summary>

**Expected answer**

    Daimler AG. [F1] [F2]

**Raw 3B**

    The Mercedes-Benz W116 automobiles were the first Mercedes-Benz models to be officially called S-Class, and the Mercedes-Benz S-Class, formerly known as Sonderklasse (German for "special class", abbreviated as "S-Klasse"), is a series of luxury flagship vehicles produced by the German automaker Mercedes-Benz, a division of German company Daimler AG.

**Fine-tuned 3B**

    Daimler AG. [F1] [F2]

</details>

<details>
<summary><strong>A66. Where is the principal of the Permanent Fund invested?</strong> — extractive_answer</summary>

**Expected answer**

    outside Alaska. [F1]

**Raw 3B**

    The principal of the Permanent Fund is invested conservatively outside Alaska.

**Fine-tuned 3B**

    conservatively outside Alaska. [F1]

</details>

<details>
<summary><strong>A67. What is dependent on the frame of refrence in Newtonian space?</strong> — unanswerable</summary>

**Expected answer**

    I do not have enough verified evidence to answer.

**Raw 3B**

    In Newtonian space, the frame of reference is independent of the objects contained within it.

**Fine-tuned 3B**

    objects. [F1]

</details>

<details>
<summary><strong>A68. When did the annexation of Naples by Italy happen?</strong> — unanswerable</summary>

**Expected answer**

    I do not have enough verified evidence to answer.

**Raw 3B**

    The annexation of Naples by Italy occurred in 1861.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A69. The WS-15, code name Emei, is a Chinese after burning turbofan engine, a stealth, twinjet, fifth-generation fighter aircraft developed by China's Chengdu Aerospace Corporation for what airforce?</strong> — grounded_qa</summary>

**Expected answer**

    People's Liberation Army Air Force. [F1]

**Raw 3B**

    The WS-15, also known as Emei, is a Chinese afterburning turbofan engine. It is used to power China's Chengdu J-20 fighter aircraft, which is a stealth, twinjet, fifth-generation fighter aircraft developed by China's Chengdu Aerospace Corporation for the People's Liberation Army Air Force (PLAAF).

**Fine-tuned 3B**

    People's Liberation Army Air Force (PLAAF). [F1]

</details>

<details>
<summary><strong>A70. Which readers was the series The Lost Journals of Ven Polypheme published for?</strong> — grounded_qa</summary>

**Expected answer**

    readers in their youth. [F1]

**Raw 3B**

    The series The Lost Journals of Ven Polypheme was published for readers in their youth, as it falls under the category of young adult fiction or young adult literature (YA).

**Fine-tuned 3B**

    readers in their youth. [F1]

</details>

<details>
<summary><strong>A71. For what TV show, is the actor who plays the role of Nardole in Doctor Who, best known ?</strong> — multi_hop</summary>

**Expected answer**

    Little Britain. [F1] [F2]

**Raw 3B**

    The actor who plays the role of Nardole in Doctor Who, Matt Lucas, is best known for his work with David Walliams in the television show "Little Britain".

**Fine-tuned 3B**

    Little Britain. [F1] [F2]

</details>

<details>
<summary><strong>A72. What slowed down the growth of solar energy?</strong> — extractive_answer</summary>

**Expected answer**

    the outbreak of World War I and the discovery of cheap oil. [F1]

**Raw 3B**

    The growth of solar energy was slowed down by the outbreak of World War I and the discovery of cheap oil in the 1930s.

**Fine-tuned 3B**

    World War I and the discovery of cheap oil in the 1930s. [F1]

</details>

<details>
<summary><strong>A73. Kevin Quinn starred in a Disney channel series which was a spinoff of what show?</strong> — grounded_qa</summary>

**Expected answer**

    Jessie. [F1]

**Raw 3B**

    Kevin Quinn starred in the Disney Channel series "Bunk'd", which was a spinoff of "Jessie".

**Fine-tuned 3B**

    Jessie. [F1]

</details>

<details>
<summary><strong>A74. What is the nickname of the boxer who was offered to fight against Sergio Martinez in Atlantic City 2011?</strong> — multi_hop</summary>

**Expected answer**

    Nicknamed "The Punisher", and standing at a height of 6 foot 1 inches, Williams was unusually tall for the three divisions in which he competed. [F1] [F2]

**Raw 3B**

    The nickname of the boxer who was offered to fight against Sergio Martínez in Atlantic City, New Jersey, in 2011 was "The Punisher".

**Fine-tuned 3B**

    The Punisher. [F1] [F2]

</details>

<details>
<summary><strong>A75. Which division does the football team, who made the playoffs for the first time in seven seasons in 2015, play within?</strong> — grounded_qa</summary>

**Expected answer**

    AFC East. [F1]

**Raw 3B**

    The football team that made the playoffs for the first time in seven seasons in 2015 plays in the AFC East division.

**Fine-tuned 3B**

    AFC East. [F1]

</details>

<details>
<summary><strong>A76. What was the focus of paintings in Italy?</strong> — extractive_answer</summary>

**Expected answer**

    idealized compositions. [F1]

**Raw 3B**

    The focus of paintings in Italy was on idealized compositions.

**Fine-tuned 3B**

    idealized compositions. [F1]

</details>

<details>
<summary><strong>A77. Indigenous people in what zones use fur for warmth and protection?</strong> — extractive_answer</summary>

**Expected answer**

    arctic. [F1]

**Raw 3B**

    Indigenous people in arctic zones and higher elevations use fur for warmth and protection.

**Fine-tuned 3B**

    arctic zones. [F1]

</details>

<details>
<summary><strong>A78. Fort Lyon was constructed south of a city whose population was what in the census of 2010?</strong> — multi_hop</summary>

**Expected answer**

    139,966. [F1] [F2]

**Raw 3B**

    Fort Lyon was constructed south of Alexandria, Virginia, which had a population of 139,966 at the 2010 census.

**Fine-tuned 3B**

    139,966. [F1] [F2]

</details>

<details>
<summary><strong>A79. What was the name of the Mexican territory San Diego became part of in 1821?</strong> — extractive_answer</summary>

**Expected answer**

    Alta California. [F1]

**Raw 3B**

    San Diego became part of the Mexican territory of Alta California in 1821.

**Fine-tuned 3B**

    Alta California. [F1]

</details>

<details>
<summary><strong>A80. What are the variances of vacuum energy according to Coulomb's law?</strong> — unanswerable</summary>

**Expected answer**

    I do not have enough verified evidence to answer.

**Raw 3B**

    I do not have enough verified evidence to answer. The evidence provided does not mention the variances of vacuum energy or how they relate to Coulomb's law.

**Fine-tuned 3B**

    I do not have enough verified evidence to answer.

</details>

<details>
<summary><strong>A81. Before the use of the cotton gin, how was cotton separated?</strong> — extractive_answer</summary>

**Expected answer**

    by hand. [F1]

**Raw 3B**

    Before the use of the cotton gin, cotton fibers were pulled from the seeds tediously by hand.

**Fine-tuned 3B**

    by hand. [F1]

</details>

<details>
<summary><strong>A82. Who rewarded contributions to the arts and sciences?</strong> — extractive_answer</summary>

**Expected answer**

    "order of chivalry of British constitutional monarchy. [F1]

**Raw 3B**

    King George V rewarded contributions to the arts and sciences.

**Fine-tuned 3B**

    King George V. [F1]

</details>

<details>
<summary><strong>A83. Chris Gould is the brother of a placekicker who played college football where?</strong> — grounded_qa</summary>

**Expected answer**

    Penn State. [F1]

**Raw 3B**

    Chris Gould is the brother of Robbie Gould, who played college football at Penn State.

**Fine-tuned 3B**

    Penn State. [F1]

</details>

<details>
<summary><strong>A84. What is the highest object of meditation called?</strong> — extractive_answer</summary>

**Expected answer**

    arūpajhānas. [F1]

**Raw 3B**

    The highest object of meditation is called arūpajhānas.

**Fine-tuned 3B**

    arūpajhānas. [F1]

</details>

<details>
<summary><strong>A85. What countries utilize strategic bomber aircraft in their missions?</strong> — extractive_answer</summary>

**Expected answer**

    US, Russia, and the People's Republic of China. [F1]

**Raw 3B**

    The US, Russia, and the People's Republic of China utilize strategic bomber aircraft in their missions.

**Fine-tuned 3B**

    US, Russia, and the People's Republic of China. [F1]

</details>

<details>
<summary><strong>A86. Who claimed responsibility for the hotel attack that killed Carsten Thomassen?</strong> — grounded_qa</summary>

**Expected answer**

    the Taliban. [F1]

**Raw 3B**

    The Taliban claimed responsibility for the hotel attack that killed Carsten Thomassen.

**Fine-tuned 3B**

    Taliban. [F1]

</details>

<details>
<summary><strong>A87. What is the birth date of this American professional basketball player, who entered the league out of high school and was a recruit to the 2004-05 Duke Blue Devil men's basketball team?</strong> — grounded_qa</summary>

**Expected answer**

    September 11, 1985. [F1]

**Raw 3B**

    Shaun Patrick Livingston was born on September 11, 1985.

**Fine-tuned 3B**

    September 11, 1985. [F1]

</details>

<details>
<summary><strong>A88. What was Victoria's unofficial title?</strong> — extractive_answer</summary>

**Expected answer**

    the grandmother of Europe. [F1]

**Raw 3B**

    Victoria's unofficial title was "the grandmother of Europe."

**Fine-tuned 3B**

    "the grandmother of Europe". [F1]

</details>

<details>
<summary><strong>A89. How ling is the bridge to the main airport in Hong Kong?</strong> — grounded_qa</summary>

**Expected answer**

    1177 m. [F1]

**Raw 3B**

    The Ting Kau Bridge is 1177 meters long.

**Fine-tuned 3B**

    1177 m. [F1]

</details>

<details>
<summary><strong>A90. Wanaka Airport no longer has scheduled commercial flights, with Air New Zealand, a company based in what city, having ceased flights to the airport in 2013?</strong> — grounded_qa</summary>

**Expected answer**

    Auckland. [F1]

**Raw 3B**

    Based on the provided evidence, Air New Zealand is based in Auckland.

**Fine-tuned 3B**

    Auckland. [F1]

</details>

<details>
<summary><strong>A91. Rabbi Yehuda Hachasid led a group of how many Jews into Jerusalem?</strong> — extractive_answer</summary>

**Expected answer**

    1,500. [F1]

**Raw 3B**

    Rabbi Yehuda Hachasid led a group of 1,500 Jews into Jerusalem.

**Fine-tuned 3B**

    1,500. [F1]

</details>

<details>
<summary><strong>A92. Which two of Feynman's colleagues helped put the lectures into book format?</strong> — extractive_answer</summary>

**Expected answer**

    Robert B. Leighton and Matthew Sands. [F1]

**Raw 3B**

    Robert B. Leighton and Matthew Sands helped put the lectures into book format.

**Fine-tuned 3B**

    Robert B. Leighton and Matthew Sands. [F1]

</details>

<details>
<summary><strong>A93. What factors sustained the beliefs in gods according to Varro?</strong> — extractive_answer</summary>

**Expected answer**

    devotion and cult. [F1]

**Raw 3B**

    According to Varro, the beliefs in gods were sustained by mortal devotion and cult.

**Fine-tuned 3B**

    devotion and cult. [F1]

</details>

<details>
<summary><strong>A94. Which actors star in the the movie that inspired Karle Pyaar Karle?</strong> — multi_hop</summary>

**Expected answer**

    Marion Cotillard and Guillaume Canet. [F1] [F2]

**Raw 3B**

    Based on the provided evidence, the movie that inspired Karle Pyaar Karle is Love Me If You Dare. The evidence states that Love Me If You Dare stars Marion Cotillard and Guillaume Canet. Therefore, Marion Cotillard and Guillaume Canet are the actors who star in the movie that inspired Karle Pyaar Karle.

**Fine-tuned 3B**

    Marion Cotillard and Guillaume Canet. [F1] [F2]

</details>

<details>
<summary><strong>A95. What actor from The Imitation Game also starred in "Revolver", "RocknRolla" and "Sherlock Holmes"?</strong> — grounded_qa</summary>

**Expected answer**

    Mark Strong. [F1]

**Raw 3B**

    Based on the provided evidence, the actor who starred in "Revolver", "RocknRolla", and "Sherlock Holmes" is Matthew Goode.

**Fine-tuned 3B**

    Matthew Goode. [F1]

</details>

<details>
<summary><strong>A96. What dynasty was founded by a Viking leader in the mid 9th century? (Info A: Viking leader founder, Info B: mid 9th century)</strong> — multi_hop</summary>

**Expected answer**

    Uí Ímair. [F1] [F2]

**Raw 3B**

    The dynasty founded by a Viking leader in the mid-9th century was the Uí Ímair dynasty. This dynasty was led by Ímar, who was a Viking leader in Ireland and Scotland during the mid-late 9th century. The Uí Ímair dynasty ruled much of the Irish Sea region, including parts of Ireland, Scotland, and Northern England.

**Fine-tuned 3B**

    Uí Ímair. [F1] [F2]

</details>

<details>
<summary><strong>A97. In what month and year was the release of the novel that "The Divergent Series: Allegiant" was based on?</strong> — multi_hop</summary>

**Expected answer**

    October 2013. [F1] [F2]

**Raw 3B**

    The novel that "The Divergent Series: Allegiant" was based on was released in October 2013.

**Fine-tuned 3B**

    October 2013. [F1] [F2]

</details>

<details>
<summary><strong>A98. When did the reign of Louis the Pious end?</strong> — extractive_answer</summary>

**Expected answer**

    840. [F1]

**Raw 3B**

    The reign of Louis the Pious ended in 840.

**Fine-tuned 3B**

    840. [F1]

</details>

<details>
<summary><strong>A99. Lisbeth Hummen stared in which 1975 French erotic fantasy horror film?</strong> — multi_hop</summary>

**Expected answer**

    La Bête. [F1] [F2]

**Raw 3B**

    Lisbeth Hummel starred in the 1975 French erotic fantasy horror film "The Beast".

**Fine-tuned 3B**

    The Beast. [F1] [F2]

</details>

<details>
<summary><strong>A100. The comedian and actor Breckiin Meyer can be seen in which movie that involves traveling 1800 miles to retrieve a tape?</strong> — grounded_qa</summary>

**Expected answer**

    Road Trip. [F1]

**Raw 3B**

    The comedian and actor Breckin Meyer can be seen in the movie "Road Trip".

**Fine-tuned 3B**

    Road Trip. [F1]

</details>

## Interpretation and limitations

- The two evaluations use different datasets and metrics; their numerical scores must not be compared as though they came from one benchmark.
- Token F1 and concept-containment scoring are lexical proxies, not semantic or expert human judgments.
- Citation validity checks whether emitted identifiers exist in the prompt; it does not prove that the cited passage entails the claim.
- The adapter comparison uses the first 100 examples from a 1,007-example held-out file. A complete evaluation remains desirable.
- Three answerable examples received false refusals, and one unanswerable example was answered incorrectly.
- The eight profile-specific questions in the 50-question run depended on an earlier/local graph state that is absent from the current committed graph snapshot.
- The correct next comparison is a read-only rerun of the same 50 questions with the new adapter loaded into the 3B+KG pipeline.

## Source artifacts

- `eval/results/accuracy/three_model_50/results.json`
- `finetune/results/grounded_v2_100_comparison.json`
- `finetune/checkpoints/qwen3b-grounded-v2/final_metrics.json`
- `finetune/checkpoints/qwen3b-grounded-v2/best-adapter/`
