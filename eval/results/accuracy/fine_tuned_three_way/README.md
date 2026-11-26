# Same-question answer comparison: cloud vs raw 3B vs fine-tuned 3B

> All three configurations answer the same 50 questions. No KG evidence is supplied in this comparison. The fine-tuned model is therefore tested outside its intended evidence-conditioned pipeline.

## Metrics

| Model | Overall | Public | Profile-specific | KG facts |
|---|---:|---:|---:|---:|
| Raw 3B | 27/50 (54.0%) | 19/30 | 1/8 | 7/12 |
| Fine-tuned 3B | 17/50 (34.0%) | 12/30 | 0/8 | 5/12 |
| Cloud 120B | 39/50 (78.0%) | 26/30 | 3/8 | 10/12 |

## Complete answer differences

<details>
<summary><strong>1. Who invented the Python programming language?</strong> — expected: GuidoVanRossum</summary>

**Raw 3B — PASS**

    Guido van Rossum created the Python programming language in 1989.

**Fine-tuned 3B — PASS**

    Guido van Rossum. [request]

**Cloud 120B — PASS**

    Python was created by Guido van Rossum, who first released it in 1991.

</details>

<details>
<summary><strong>2. Who invented JavaScript?</strong> — expected: BrendanEich</summary>

**Raw 3B — PASS**

    Brendan Eich created JavaScript while working at Netscape Communications Corporation in 1995.

**Fine-tuned 3B — PASS**

    Brendan Eich. [request]

**Cloud 120B — PASS**

    JavaScript was invented by Brendan Eich in 1995 while he was working at Netscape.

</details>

<details>
<summary><strong>3. Who developed TypeScript?</strong> — expected: AndersHejlsberg</summary>

**Raw 3B — FAIL**

    TypeScript was developed by Microsoft as an open-source programming language that adds static typing to JavaScript, enhancing its capabilities for large-scale applications.

**Fine-tuned 3B — FAIL**

    Microsoft. [link]

**Cloud 120B — PASS**

    TypeScript was developed by Microsoft, primarily authored by Anders Hejlsberg.

</details>

<details>
<summary><strong>4. Who developed the Java programming language?</strong> — expected: JamesGosling</summary>

**Raw 3B — PASS**

    James Gosling developed the Java programming language.

**Fine-tuned 3B — PASS**

    James Gosling. [request]

**Cloud 120B — PASS**

    The Java programming language was developed by James Gosling and his team at Sun Microsystems.

</details>

<details>
<summary><strong>5. Who invented C++?</strong> — expected: BjarneStroustrup</summary>

**Raw 3B — PASS**

    Bjarne Stroustrup developed C++.

**Fine-tuned 3B — PASS**

    Bjarne Stroustrup. [request]

**Cloud 120B — PASS**

    C++ was invented by Bjarne Stroustrup in the early 1980s.

</details>

<details>
<summary><strong>6. Who invented the Rust programming language?</strong> — expected: GraydonHoare</summary>

**Raw 3B — PASS**

    Graydon Hoare invented the Rust programming language.

**Fine-tuned 3B — PASS**

    Graydon Hoare. [link]

**Cloud 120B — PASS**

    The Rust programming language was invented by Graydon Hoare while working at Mozilla.

</details>

<details>
<summary><strong>7. Who developed the Swift programming language?</strong> — expected: ChrisLattner</summary>

**Raw 3B — FAIL**

    Apple Inc. developed the Swift programming language.

**Fine-tuned 3B — FAIL**

    Apple Inc. [Citations needed]

**Cloud 120B — PASS**

    Swift was developed by Apple, led by Chris Lattner and his team.

</details>

<details>
<summary><strong>8. Who invented the Ruby programming language?</strong> — expected: YukihiroMatsumoto</summary>

**Raw 3B — PASS**

    Yukihiro Matsumoto created Ruby in 1995 as a dynamic, object-oriented scripting language influenced by Perl, Smalltalk, Lisp, and C.

**Fine-tuned 3B — PASS**

    Yukihiro Matsumoto. [request]

**Cloud 120B — PASS**

    Yukihiro “Matz” Matsumoto invented the Ruby programming language.

</details>

<details>
<summary><strong>9. Who developed the Scala programming language?</strong> — expected: MartinOdersky</summary>

**Raw 3B — PASS**

    Martin Odersky developed the Scala programming language.

**Fine-tuned 3B — PASS**

    Martin Odersky. [requestInfo]

**Cloud 120B — PASS**

    Scala was developed by Martin Odersky and his team at the École Polytechnique Fédérale de Lausanne (EPFL).

</details>

<details>
<summary><strong>10. Who developed the Perl programming language?</strong> — expected: LarryWall</summary>

**Raw 3B — PASS**

    Larry Wall created Perl, a high-level programming language designed for text processing and web applications.

**Fine-tuned 3B — PASS**

    Larry Wall. [Source]

**Cloud 120B — PASS**

    Larry Wall developed the Perl programming language.

</details>

<details>
<summary><strong>11. Who invented the Lua programming language?</strong> — expected: RobertoIerusalimschy</summary>

**Raw 3B — FAIL**

    Brendan Eich created Lua, a lightweight scripting language designed for embedded systems and rapid application development.

**Fine-tuned 3B — FAIL**

    Roberto Ierusalimsky. [Source]

**Cloud 120B — PASS**

    Lua was invented by Roberto Ierusalimschy, Luiz Henrique de Figueiredo, and Waldemar Celes at Brazil’s Pontifical Catholic University of Rio de Janeiro.

</details>

<details>
<summary><strong>12. Who developed the Julia programming language?</strong> — expected: JeffBezanson</summary>

**Raw 3B — PASS**

    Julia was developed by Jeff Bezanson, Alan Edelman, Stefan Karpinski, and Viral Shah.

**Fine-tuned 3B — FAIL**

    Tommy Robertson. [Source]

**Cloud 120B — PASS**

    The Julia programming language was developed by a team of researchers including Jeff Bezanson, Stefan Karpinski, Viral B. Shah, and Alan Edelman.

</details>

<details>
<summary><strong>13. Who developed the Fortran programming language?</strong> — expected: JohnBackus</summary>

**Raw 3B — PASS**

    John Backus developed the Fortran programming language.

**Fine-tuned 3B — PASS**

    John Backus. [requestInfo]

**Cloud 120B — PASS**

    Fortran was developed by a team at IBM led by John Backus in the 1950s.

</details>

<details>
<summary><strong>14. Who invented Pascal?</strong> — expected: NiklausWirth</summary>

**Raw 3B — FAIL**

    Blaise Pascal, a French mathematician, physicist, and philosopher, is credited with inventing the first mechanical calculator called the Pascaline around 1642.

**Fine-tuned 3B — FAIL**

    Blaise Pascal. [request]

**Cloud 120B — FAIL**

    Pascal was invented by the Swiss mathematician and philosopher Blaise Pascal in the 17th century.

</details>

<details>
<summary><strong>15. Who developed Prolog?</strong> — expected: AlainColmerauer</summary>

**Raw 3B — PASS**

    Prolog was developed by Alain Colmerauer at the University of Paris in 1972.

**Fine-tuned 3B — PASS**

    Alain Colmerauer. [request]

**Cloud 120B — PASS**

    Prolog was developed by Alain Colmerauer and his team at the University of Marseille in the early 1970s.

</details>

<details>
<summary><strong>16. Who invented Lisp?</strong> — expected: JohnMcCarthy</summary>

**Raw 3B — PASS**

    John McCarthy invented Lisp, a programming language developed at MIT in the 1950s.

**Fine-tuned 3B — PASS**

    John McCarthy. [request]

**Cloud 120B — PASS**

    Lisp was invented by John McCarthy in 1958 while he was a professor at the Massachusetts Institute of Technology (MIT).

</details>

<details>
<summary><strong>17. Who developed Clojure?</strong> — expected: RichHickey</summary>

**Raw 3B — PASS**

    Rich Hickey developed Clojure.

**Fine-tuned 3B — PASS**

    Rich Hickey. [link]

**Cloud 120B — PASS**

    Clojure was developed by Rich Hickey.

</details>

<details>
<summary><strong>18. Who developed the F# programming language?</strong> — expected: DonSyme</summary>

**Raw 3B — FAIL**

    The F# programming language was developed by Microsoft Research.

**Fine-tuned 3B — FAIL**

    Microsoft. [request]

**Cloud 120B — PASS**

    F# was developed by Microsoft Research, primarily led by Don Syme.

</details>

<details>
<summary><strong>19. Who developed OCaml?</strong> — expected: XavierLeroy</summary>

**Raw 3B — PASS**

    OCaml was developed by Xavier Leroy at INRIA, France.

**Fine-tuned 3B — FAIL**

    Yaron Minsky. [Source]

**Cloud 120B — FAIL**

    OCaml was developed by the Caml research team at INRIA (the French Institute for Research in Computer Science and Automation).

</details>

<details>
<summary><strong>20. Who developed the Bash shell?</strong> — expected: BrianFox</summary>

**Raw 3B — FAIL**

    Bash was developed by Brian Kernighan and Dennis Ritchie at Bell Labs in 1973.

**Fine-tuned 3B — FAIL**

    Bash was developed by Brian Kernighan and Dennis Ritchie. [A]

**Cloud 120B — PASS**

    The Bash shell was developed by Brian Fox for the GNU Project in 1989.

</details>

<details>
<summary><strong>21. Who developed the Awk programming language?</strong> — expected: AlfredAho | PeterWeinberger | BrianKernighan</summary>

**Raw 3B — FAIL**

    The Awk programming language was developed by Brian Kernighan and Dennis Ritchie at Bell Labs in 1976.

**Fine-tuned 3B — FAIL**

    Brian Kernighan and Dennis Ritchie. [link]

**Cloud 120B — PASS**

    Awk was developed by Alfred Aho, Peter Weinberger, and Brian Kernighan at Bell Labs.

</details>

<details>
<summary><strong>22. Who developed Sed?</strong> — expected: LeeMcMahon</summary>

**Raw 3B — FAIL**

    Sed was developed by Bill Joy at Sun Microsystems in 1973.

**Fine-tuned 3B — FAIL**

    Sed was developed by Richard Stallman. [request]

**Cloud 120B — PASS**

    Sed was developed by Lee E. McMahon at Bell Labs.

</details>

<details>
<summary><strong>23. Who developed Matlab?</strong> — expected: CleveMoler</summary>

**Raw 3B — FAIL**

    MathWorks developed MATLAB.

**Fine-tuned 3B — FAIL**

    MathWorks. [Source]

**Cloud 120B — PASS**

    MATLAB was developed by Cleve Moler and his team at the University of New Mexico, later commercialized by the company MathWorks.

</details>

<details>
<summary><strong>24. Who developed the Scheme programming language?</strong> — expected: GeraldJaySussman</summary>

**Raw 3B — PASS**

    The Scheme programming language was developed by Guy Lewis Steele Jr. and Gerald Jay Sussman at MIT's AI Lab in the 1970s.

**Fine-tuned 3B — FAIL**

    Guy Steele. [Source]

**Cloud 120B — PASS**

    Scheme was developed at MIT in the 1970s by Guy L. Steele and Gerald Jay Sussman.

</details>

<details>
<summary><strong>25. Who developed the BubbleSort algorithm?</strong> — expected: EdwardHarryFriendJr</summary>

**Raw 3B — FAIL**

    The BubbleSort algorithm was developed by Tony Hoare in 1956.

**Fine-tuned 3B — FAIL**

    Charles Babbage. [requestInfo]

**Cloud 120B — FAIL**

    Bubble Sort was first described by computer scientist John von Neumann in 1956.

</details>

<details>
<summary><strong>26. Who developed the MergeSort algorithm?</strong> — expected: JohnVonNeumann</summary>

**Raw 3B — PASS**

    MergeSort was developed by John von Neumann in 1945.

**Fine-tuned 3B — FAIL**

    Donald Knuth. [request]

**Cloud 120B — PASS**

    Merge sort was developed by John von Neumann in 1945.

</details>

<details>
<summary><strong>27. Who developed QuickSort?</strong> — expected: TonyHoare</summary>

**Raw 3B — PASS**

    QuickSort was developed by Tony Hoare in 1959.

**Fine-tuned 3B — FAIL**

    Cormen, Thomas H. [1]

**Cloud 120B — PASS**

    QuickSort was developed by British computer scientist Tony Hoare in 1960.

</details>

<details>
<summary><strong>28. Who developed TimSort?</strong> — expected: TimPeters</summary>

**Raw 3B — FAIL**

    TimSort was developed by Python's creator, Guido van Rossum.

**Fine-tuned 3B — FAIL**

    Timothy Peter van Leeuwenhoek. [link]

**Cloud 120B — PASS**

    TimSort was developed by Tim Peters in 2002.

</details>

<details>
<summary><strong>29. What problem does Dijkstra's algorithm solve?</strong> — expected: ShortestPathProblem</summary>

**Raw 3B — PASS**

    Dijkstra's algorithm solves the single-source shortest path problem, finding the shortest path from a source node to all other nodes in a weighted graph.

**Fine-tuned 3B — FAIL**

    finding the shortest path between two nodes in a graph.

**Cloud 120B — FAIL**

    Dijkstra's algorithm finds the shortest‑path distances from a single source vertex to all other vertices in a weighted graph with non‑negative edge weights.

</details>

<details>
<summary><strong>30. What problem does the Edmonds-Karp algorithm solve?</strong> — expected: MaximumFlowProblem</summary>

**Raw 3B — PASS**

    The Edmonds-Karp algorithm solves the maximum flow problem by finding the shortest augmenting path between source and sink nodes in a network, repeatedly updating the flow until no more augmenting paths exist.

**Fine-tuned 3B — FAIL**

    maximum flow.

**Cloud 120B — PASS**

    The Edmonds‑Karp algorithm solves the maximum‑flow problem by finding the greatest possible flow from a source to a sink in a capacitated network.

</details>

<details>
<summary><strong>31. What academic position does Prasanna Kumar hold?</strong> — expected: AssociateProfessor</summary>

**Raw 3B — FAIL**

    Prasanna Kumar holds the position of Professor at the Indian Institute of Technology, Madras.

**Fine-tuned 3B — FAIL**

    Professor of Mathematics. [Source: Wikipedia]

**Cloud 120B — PASS**

    Prasanna Kumar is an Associate Professor in the Department of Computer Science and Engineering at the Indian Institute of Technology Delhi.

</details>

<details>
<summary><strong>32. Which courses does Prasanna Kumar teach?</strong> — expected: DataStructures | Algorithms</summary>

**Raw 3B — PASS**

    Prasanna Kumar teaches Computer Science, Data Structures, Algorithms, and Machine Learning at the University of California, Berkeley.

**Fine-tuned 3B — FAIL**

    Prasanna Kumar teaches Computer Science, Mathematics, and Physics. [Source: Wikipedia]

**Cloud 120B — FAIL**

    I’m sorry, but I don’t have information on the courses taught by Prasanna Kumar.

</details>

<details>
<summary><strong>33. Whom does Prasanna Kumar supervise?</strong> — expected: PhDStudents</summary>

**Raw 3B — FAIL**

    Prasanna Kumar supervises the Chief Executive Officer (CEO) of a multinational corporation.

**Fine-tuned 3B — FAIL**

    Rajesh Kishan. [Source]

**Cloud 120B — PASS**

    Prasanna Kumar supervises his graduate (PhD/Master’s) students.

</details>

<details>
<summary><strong>34. What are Prasanna Kumar's research interests?</strong> — expected: MachineLearning | DistributedSystems</summary>

**Raw 3B — FAIL**

    Prasanna Kumar's research interests include machine learning, computer vision, and natural language processing.

**Fine-tuned 3B — FAIL**

    machine learning, deep learning, computer vision. [request]

**Cloud 120B — FAIL**

    Prasanna Kumar’s research interests focus on algorithm design and analysis, particularly in graph algorithms, combinatorial optimization, and their applications to network science and data mining.

</details>

<details>
<summary><strong>35. What paper did Prasanna Kumar publish?</strong> — expected: DeepLearningForIoT</summary>

**Raw 3B — FAIL**

    Prasanna Kumar published "A New Approach to the Study of Indian History."

**Fine-tuned 3B — FAIL**

    "Prasanna Kumar: A Study of the Indian Economy".

**Cloud 120B — FAIL**

    Prasanna Kumar published the paper titled “A Study on the Performance of the Hybrid Genetic Algorithm for Solving the Traveling Salesman Problem.”

</details>

<details>
<summary><strong>36. What award did Prasanna Kumar receive?</strong> — expected: BestTeacherAward2022</summary>

**Raw 3B — FAIL**

    Prasanna Kumar received the Padma Shri, India's fourth-highest civilian honor, for his contributions to science and technology.

**Fine-tuned 3B — FAIL**

    Nobel Prize. [request]

**Cloud 120B — FAIL**

    Prasanna Kumar was honored with the Shanti Swarup Bhatnagar Prize for Science and Technology.

</details>

<details>
<summary><strong>37. Where does Prasanna Kumar reside?</strong> — expected: Chennai</summary>

**Raw 3B — FAIL**

    Prasanna Kumar resides in Bangalore, Karnataka, India.

**Fine-tuned 3B — FAIL**

    Karnataka, India. [request]

**Cloud 120B — FAIL**

    I’m sorry, but I don’t have any publicly available information about Prasanna Kumar’s place of residence.

</details>

<details>
<summary><strong>38. Which professional organizations is Prasanna Kumar a member of?</strong> — expected: IEEE | ACM</summary>

**Raw 3B — FAIL**

    Prasanna Kumar is a member of the Indian Institute of Management (IIM) Ahmedabad, the National Academy of Engineering (NAE), and the American Society for Mechanical Engineers (ASME).

**Fine-tuned 3B — FAIL**

    American Society for Quality, International Organization of Standards. [Source]

**Cloud 120B — PASS**

    Prasanna Kumar is a member of the IEEE, the ACM, and the SPIE professional societies.

</details>

<details>
<summary><strong>39. Which languages did Pascal influence?</strong> — expected: Modula2 | Ada</summary>

**Raw 3B — FAIL**

    Pascal influenced the development of several programming languages, including C, Java, and Fortran.

**Fine-tuned 3B — FAIL**

    French, English. [request]

**Cloud 120B — PASS**

    Pascal influenced several languages, notably Algol 60, Modula‑2, Ada, Oberon, and later educational and teaching languages such as Delphi/Object Pascal, as well as contributing concepts to C, Java, and many modern structured and object‑oriented languages.

</details>

<details>
<summary><strong>40. Which company developed Turbo Pascal?</strong> — expected: Borland</summary>

**Raw 3B — PASS**

    Turbo Pascal was developed by Borland International.

**Fine-tuned 3B — PASS**

    Borland. [link]

**Cloud 120B — PASS**

    Turbo Pascal was developed by Borland.

</details>

<details>
<summary><strong>41. Which two core mechanisms does Prolog support?</strong> — expected: Backtracking | Unification</summary>

**Raw 3B — PASS**

    Prolog supports backtracking and unification as its core mechanisms.

**Fine-tuned 3B — PASS**

    unification and backtracking. [request]

**Cloud 120B — PASS**

    Prolog’s core mechanisms are unification (pattern matching of terms) and backtracking (systematic search through alternative solutions).

</details>

<details>
<summary><strong>42. Name two areas where OCaml is used.</strong> — expected: CompilerConstruction | FormalVerification</summary>

**Raw 3B — FAIL**

    OCaml is primarily used for developing web applications, particularly those requiring high performance and scalability. It is also widely used in scientific computing and data analysis due to its strong type system and efficient execution.

**Fine-tuned 3B — FAIL**

    web development, scientific computing.

**Cloud 120B — FAIL**

    OCaml is widely used in formal verification (e.g., the Coq proof assistant) and in financial technology for building high‑performance trading and risk‑analysis systems.

</details>

<details>
<summary><strong>43. Which simulation product is included in MATLAB?</strong> — expected: Simulink</summary>

**Raw 3B — PASS**

    Simulink is a simulation product included in MATLAB.

**Fine-tuned 3B — PASS**

    Simulink. [requestInfo]

**Cloud 120B — PASS**

    MATLAB includes the Simulink simulation product for modeling, simulating, and analyzing dynamic systems.

</details>

<details>
<summary><strong>44. Which partitioning technique does Quicksort use?</strong> — expected: Partitioning</summary>

**Raw 3B — PASS**

    Quicksort uses the Lomuto partitioning scheme, which selects a pivot element and partitions the array around it to sort elements less than and greater than the pivot.

**Fine-tuned 3B — PASS**

    Quicksort uses the Lomuto partitioning scheme. [Source: Wikipedia]

**Cloud 120B — PASS**

    Quicksort uses **divide‑and‑conquer partitioning**, repeatedly splitting the array into elements less than a chosen pivot and elements greater than the pivot.

</details>

<details>
<summary><strong>45. Is Quicksort a stable sorting algorithm?</strong> — expected: notstable</summary>

**Raw 3B — PASS**

    No, Quicksort is not a stable sorting algorithm.

**Fine-tuned 3B — FAIL**

    no. [request]

**Cloud 120B — PASS**

    No; Quicksort is not a stable sorting algorithm unless specifically modified to preserve the relative order of equal elements.

</details>

<details>
<summary><strong>46. Name two areas where Lua is used.</strong> — expected: GameDevelopment | EmbeddedSystems</summary>

**Raw 3B — FAIL**

    Lua is primarily used for game scripting, particularly in the development of video games, and as a server-side language for web applications.

**Fine-tuned 3B — FAIL**

    server-side scripting, game development.

**Cloud 120B — PASS**

    Lua is commonly used in game development (e.g., scripting game logic) and embedded systems for configuration or automation tasks.

</details>

<details>
<summary><strong>47. What does clean cooking reduce?</strong> — expected: IndoorAirPollution</summary>

**Raw 3B — FAIL**

    Clean cooking reduces the risk of foodborne illnesses by minimizing exposure to harmful bacteria, chemicals, and pollutants during the preparation process.

**Fine-tuned 3B — FAIL**

    smoke. [request]

**Cloud 120B — PASS**

    Clean cooking reduces indoor air pollution, greenhouse‑gas emissions, and associated health risks.

</details>

<details>
<summary><strong>48. What does water sanitation improve?</strong> — expected: PublicHealth</summary>

**Raw 3B — PASS**

    Water sanitation improves public health by reducing the spread of diseases through contaminated water sources.

**Fine-tuned 3B — FAIL**

    health. [request]

**Cloud 120B — PASS**

    Water sanitation improves public health by reducing disease transmission, preventing water‑borne illnesses, and promoting safer drinking water and hygiene.

</details>

<details>
<summary><strong>49. What does rural electrification improve?</strong> — expected: EducationOutcomes</summary>

**Raw 3B — FAIL**

    Rural electrification improves access to electricity, reducing energy poverty, improving health outcomes, enhancing agricultural productivity, and fostering economic development.

**Fine-tuned 3B — FAIL**

    access to electricity. [request]

**Cloud 120B — FAIL**

    Rural electrification improves household living standards, economic productivity, education, healthcare services, and overall community development.

</details>

<details>
<summary><strong>50. What does deforestation contribute to?</strong> — expected: ClimateChange</summary>

**Raw 3B — PASS**

    Deforestation contributes to climate change by releasing stored carbon dioxide into the atmosphere, altering local ecosystems, and reducing biodiversity.

**Fine-tuned 3B — PASS**

    climate change. [request]

**Cloud 120B — PASS**

    Deforestation contributes to climate change by releasing stored carbon dioxide, loss of biodiversity, soil erosion, and disruption of water cycles.

</details>
