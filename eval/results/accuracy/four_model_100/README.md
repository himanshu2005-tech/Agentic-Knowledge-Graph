# 100-question four-model evaluation

> Same held-out questions and expected answers. Both KG configurations receive the same evidence. Raw 3B and cloud 120B receive only the question.

## Overall metrics

| Configuration | Mean token F1 | Exact matches | Refusal recall | False refusals |
|---|---:|---:|---:|---:|
| Raw 3B | 0.0840 | 0/100 | 0.0% | 0 |
| Raw 3B + KG | 0.2281 | 1/100 | 18.2% | 1 |
| Fine-tuned 3B + KG | 0.8747 | 74/100 | 90.9% | 3 |
| Cloud 120B | 0.1056 | 0/100 | 0.0% | 0 |

## Paired fine-tuned 3B + KG improvement

| Baseline | Mean F1 delta | Bootstrap 95% interval | Wins / ties / losses |
|---|---:|---:|---:|
| Raw 3B | +0.7907 | [+0.7281, +0.8475] | 95 / 2 / 3 |
| Raw 3B + KG | +0.6466 | [+0.5851, +0.7049] | 94 / 2 / 4 |
| Cloud 120B | +0.7691 | [+0.7051, +0.8272] | 94 / 2 / 4 |

## Category-level mean token F1

| Configuration | Extractive | Grounded QA | Multi-hop | Unanswerable |
|---|---:|---:|---:|---:|
| Raw 3B | 0.1127 | 0.0670 | 0.0839 | 0.0335 |
| Raw 3B + KG | 0.3004 | 0.2123 | 0.1662 | 0.1722 |
| Fine-tuned 3B + KG | 0.8307 | 0.9071 | 0.8866 | 0.9091 |
| Cloud 120B | 0.1059 | 0.1125 | 0.1227 | 0.0486 |

## Complete answers

<details>
<summary><strong>Q1. How often is Politics & Policy not published?</strong> — unanswerable</summary>

**Expected**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Politics & Policy is typically published quarterly, but it may be delayed due to various factors such as editorial decisions or changes in publication schedules.

**Raw 3B + KG**

    Politics & Policy is published several times a week.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    Politics & Policy is published quarterly, so it is not published three times each year.

</details>

<details>
<summary><strong>Q2. Masjid al-Qiblatayn, is a mosque in which city, situated in the northwestern Awdal region of Somaliland, officially the Republic of Somaliland, is a self-declared state internationally recognised as an autonomous region of Somalia?</strong> — grounded_qa</summary>

**Expected**

    Zeila. [F1]

**Raw 3B**

    Masjid al-Qiblatayn is located in Hargeisa, the capital city of Somaliland.

**Raw 3B + KG**

    Masjid al-Qiblatayn is located in Zeila, which is situated in the northwestern Awdal region of Somaliland. Somaliland is an internationally recognised state that is self-declared and is an autonomous region of Somalia.

**Fine-tuned 3B + KG**

    Zeila. [F1]

**Cloud 120B**

    Masjid al‑Qiblatayn is located in the city of Borama.

</details>

<details>
<summary><strong>Q3. How many people identify as gay or bisexual in NYC?</strong> — extractive_answer</summary>

**Expected**

    568,903. [F1]

**Raw 3B**

    According to recent surveys, approximately 10% of New Yorkers identify as gay or bisexual.

**Raw 3B + KG**

    According to the evidence provided, approximately 568,903 individuals in the New York metropolitan area identify as gay or bisexual. This figure represents the largest self-identifying gay and bisexual community in the United States and one of the world's largest.

**Fine-tuned 3B + KG**

    568,903. [F1]

**Cloud 120B**

    According to recent estimates from the NYC Department of Health and the 2022 Gallup poll, roughly 10‑12 percent of New York City’s adult population—about 800,000 to 1 million people—identify as gay, lesbian, or bisexual.

</details>

<details>
<summary><strong>Q4. Hangman stars what actress who began her acting career in "Campfire Tales"?</strong> — multi_hop</summary>

**Expected**

    Amy Smart. [F1] [F2]

**Raw 3B**

    The Hangman stars Jennifer Lawrence, who began her acting career in the 1987 film "Campfire Tales."

**Raw 3B + KG**

    Hangman stars Amy Smart, who began her acting career in "Campfire Tales."

**Fine-tuned 3B + KG**

    Amy Smart. [F1] [F2]

**Cloud 120B**


</details>

<details>
<summary><strong>Q5. Who was the showrunner for the Simpsons season with the episode spoofing Cape Fear?</strong> — grounded_qa</summary>

**Expected**

    David Mirkin. [F1]

**Raw 3B**

    The showrunner for the Simpsons season featuring the episode "Cape Fear" was Matt Selman.

**Raw 3B + KG**

    The showrunner for the Simpsons season that featured the episode "Cape Feare", which is a spoof of the 1962 film "Cape Fear", was David Mirkin.

**Fine-tuned 3B + KG**

    David Mirkin. [F1]

**Cloud 120B**

    The season 5 episode “Cape Feare” was overseen by showrunners Al Jean and Mike Reiss.

</details>

<details>
<summary><strong>Q6. Innovative Life: The Anthology 1984-1989, is a compilation album released in 2008 by who, which American rapper, singer-songwriter, record producer and DJ?</strong> — grounded_qa</summary>

**Expected**

    Arabian Prince. [F1]

**Raw 3B**

    The Anthology 1984-1989 was released by Jay-Z.

**Raw 3B + KG**

    Innovative Life: The Anthology 1984-1989 is a compilation album released in 2008 by American recording artist Arabian Prince. Kim Renard Nazel, better known by the stage name Arabian Prince, is an American rapper, singer-songwriter, record producer, and DJ.

**Fine-tuned 3B + KG**

    Arabian Prince. [F1]

**Cloud 120B**

    It was released in 2008 by American rapper, singer‑songwriter, record producer and DJ Prince Paul.

</details>

<details>
<summary><strong>Q7. Which genre did Madonna started out in?</strong> — extractive_answer</summary>

**Expected**

    rock music. [F1]

**Raw 3B**

    Madonna began her career as a pop singer before transitioning into the music video industry.

**Raw 3B + KG**

    Madonna started out in rock music.

**Fine-tuned 3B + KG**

    rock. [F1]

**Cloud 120B**

    Madonna began her career as a pop artist, emerging in the early 1980s with dance‑oriented pop music.

</details>

<details>
<summary><strong>Q8. Which film director is younger, Del Lord or Wang Xiaoshuai?</strong> — grounded_qa</summary>

**Expected**

    Del Lord. [F1]

**Raw 3B**

    Wang Xiaoshuai is younger than Del Lord by approximately 10 years.

**Raw 3B + KG**

    Wang Xiaoshuai is younger than Del Lord. Wang Xiaoshuai was born on May 22, 1966, while Del Lord was born on October 7, 1894.

**Fine-tuned 3B + KG**

    Wang Xiaoshuai. [F1]

**Cloud 120B**

    Wang Xiaoshuai is younger.

</details>

<details>
<summary><strong>Q9. In how many countries, was this 2-seater hatchback Microcar manufactured and marketed by this group led by Annette Winkler?</strong> — multi_hop</summary>

**Expected**

    46 countries. [F1] [F2]

**Raw 3B**

    The Microcar was manufactured and marketed by the group led by Annette Winkler in 10 countries.

**Raw 3B + KG**

    The Smart Fortwo was marketed in 46 countries worldwide.

**Fine-tuned 3B + KG**

    46. [F1] [F2]

**Cloud 120B**

    The Microcar 2‑seater hatchback was manufactured and marketed in **12 countries**.

</details>

<details>
<summary><strong>Q10. Who was Joseph's father?</strong> — extractive_answer</summary>

**Expected**

    Jacob. [F1]

**Raw 3B**

    Joseph's father was Jacob.

**Raw 3B + KG**

    According to the evidence provided, Joseph's father was Jacob.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    Joseph’s father was Jacob.

</details>

<details>
<summary><strong>Q11. Which rap duo includes a performer who starred in "Sol Goode"?</strong> — multi_hop</summary>

**Expected**

    The Wow. [F1] [F2]

**Raw 3B**

    The rap duo featuring a star from "Sol Goode" is The Notorious B.I.G.

**Raw 3B + KG**

    The rap duo that includes a performer who starred in "Sol Goode" is The Wow. According to the evidence provided, Balthazar Getty, who starred in "Sol Goode," is a member of the rap duo The Wow.

**Fine-tuned 3B + KG**

    The Wow. [F1] [F2]

**Cloud 120B**


</details>

<details>
<summary><strong>Q12. What strip club-related law were the council members trying to repeat?</strong> — unanswerable</summary>

**Expected**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Council members sought to replicate a ban on strippers that had been struck down by the Supreme Court.

**Raw 3B + KG**

    The council members were trying to repeat the city's "no touch" laws at strip clubs.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    They were trying to reenact the city’s “no‑strip‑club within 500 feet of a school” ordinance.

</details>

<details>
<summary><strong>Q13. You're No Good: was covered in a charting version by which soul singer and pianist?</strong> — multi_hop</summary>

**Expected**

    Betty Everett. [F1] [F2]

**Raw 3B**

    You're No Good was covered in a charting version by James Brown.

**Raw 3B + KG**

    You're No Good was covered in a charting version by Betty Everett.

**Fine-tuned 3B + KG**

    Betty Everett. [F1] [F2]

**Cloud 120B**


</details>

<details>
<summary><strong>Q14. What organization commented on the deal between EMC and Dell?</strong> — extractive_answer</summary>

**Expected**

    FBR Capital Markets. [F1]

**Raw 3B**

    The Wall Street Journal commented on the deal between EMC and Dell.

**Raw 3B + KG**

    The organizations that commented on the deal between EMC and Dell include:
    
    1. FBR Capital Markets
    2. Fortune
    3. The Register
    4. William Blair & Company
    
    These commenters expressed varying opinions about the deal, with some praising its potential benefits while others expressing concerns about strategic synergies and market impact.

**Fine-tuned 3B + KG**

    Commentators. [F1]

**Cloud 120B**

    The European Commission’s competition directorate commented on the Dell‑EMC deal.

</details>

<details>
<summary><strong>Q15. Where does the American singer-songwriter, Vic Chessnutt, who features on an album of covers of Gram Parsons' songs, hail from?</strong> — grounded_qa</summary>

**Expected**

    Athens, Georgia. [F1]

**Raw 3B**

    Vic Chessnutt hails from New York City.

**Raw 3B + KG**

    Vic Chesnutt hails from Athens, Georgia.

**Fine-tuned 3B + KG**

    Athens, Georgia. [F1]

**Cloud 120B**

    Vic Chesnutt hailed from Athens, Georgia.

</details>

<details>
<summary><strong>Q16. What did System R avoid to change the way data was stored?</strong> — unanswerable</summary>

**Expected**

    I do not have enough verified evidence to answer.

**Raw 3B**

    System R avoided changing the way data was stored by focusing on improving query performance rather than altering the underlying storage model.

**Raw 3B + KG**

    System R avoided changing the way data was stored by keeping it in a single large "chunk" for each record.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    System R avoided tying the database schema to a fixed physical storage format, instead using logical data independence to keep the way data was stored separate from how it was defined.

</details>

<details>
<summary><strong>Q17. What describes the connection between the conditions of cyclic existence?</strong> — extractive_answer</summary>

**Expected**

    The Twelve Nidānas. [F1]

**Raw 3B**

    The conditions of cyclic existence describe a repeating pattern or cycle that repeats indefinitely, often with specific starting and ending points.

**Raw 3B + KG**

    The Twelve Nidānas describe a causal connection between the subsequent conditions or characteristics of cyclic existence, each one giving rise to the next.

**Fine-tuned 3B + KG**

    The Twelve Nidānas. [F1]

**Cloud 120B**

    The doctrine of dependent (or conditioned) origination describes the inter‑connected chain of conditions that give rise to cyclic existence.

</details>

<details>
<summary><strong>Q18. How many Americans were found to have intermediate health literacy?</strong> — extractive_answer</summary>

**Expected**

    44%. [F1]

**Raw 3B**

    According to a 2014 study, approximately 35% of American adults had intermediate health literacy.

**Raw 3B + KG**

    According to the evidence provided, 44% of adult Americans were found to have intermediate health literacy.

**Fine-tuned 3B + KG**

    44%. [F1]

**Cloud 120B**

    According to the referenced study, 34 % of Americans were found to have intermediate health literacy.

</details>

<details>
<summary><strong>Q19. What restriction does W-VHS recordings have?</strong> — extractive_answer</summary>

**Expected**

    analog only. [F1]

**Raw 3B**

    W-VHS recordings are restricted to 1 hour per side due to the physical limitations of the tape format.

**Raw 3B + KG**

    W-VHS recordings are analog-only.

**Fine-tuned 3B + KG**

    analog only. [F1]

**Cloud 120B**

    W‑VHS recordings are restricted to playback only on compatible W‑VHS equipment and cannot be duplicated or transferred to other formats.

</details>

<details>
<summary><strong>Q20. What military forces usually integrate air defnce as a separate arm or part of artillery?</strong> — extractive_answer</summary>

**Expected**

    Western and Commonwealth militaries. [F1]

**Raw 3B**

    The United States Army, the Royal Air Force, and some other NATO countries typically integrate air defense as a separate arm or part of artillery.

**Raw 3B + KG**

    Most Western and Commonwealth militaries integrate air defence as a separate arm or part of artillery.

**Fine-tuned 3B + KG**

    Most Western and Commonwealth militaries. [F1]

**Cloud 120B**

    Most militaries integrate air defense as a separate branch (e.g., the U.S. Army’s Air Defense Artillery, Russia’s Aerospace Forces, and China’s PLA Air Defense Force), while others embed it within artillery units (such as Germany’s Luftabwehrtruppen and many NATO armies).

</details>

<details>
<summary><strong>Q21. How many downloads did the lead single from Over My Head get as of January 2015?</strong> — multi_hop</summary>

**Expected**

    4.7 million. [F1] [F2]

**Raw 3B**

    The lead single from Over My Head received over 3 million downloads as of January 2015.

**Raw 3B + KG**

    According to the evidence provided, the lead single from "Over My Head" (which was originally titled "Cable Car") received 4.7 million downloads as of January 2015.

**Fine-tuned 3B + KG**

    4.7 million. [F1] [F2]

**Cloud 120B**

    The lead single “Over My Head (Cable Car)” had been downloaded about 2.5 million times by January 2015.

</details>

<details>
<summary><strong>Q22. Who has the power and right to enact statutes for interstate dealings?</strong> — extractive_answer</summary>

**Expected**

    Congress. [F1]

**Raw 3B**

    The federal government has the power and right to enact statutes for interstate dealings through its constitutional authority over commerce.

**Raw 3B + KG**

    Congress has the power and right to enact statutes for interstate dealings.

**Fine-tuned 3B + KG**

    Congress. [F1]

**Cloud 120B**

    The U.S. Congress, exercising its constitutional authority under the Commerce Clause, has the power and right to enact statutes governing interstate dealings.

</details>

<details>
<summary><strong>Q23. What is an example of a brewer that owns pubs throughout Britain?</strong> — extractive_answer</summary>

**Expected**

    Greene King. [F1]

**Raw 3B**

    Brewer John Smith owns pubs across Britain, including The Old Brewery in London and The Crown in Edinburgh.

**Raw 3B + KG**

    An example of a brewer that owns pubs throughout Britain is Greene King.

**Fine-tuned 3B + KG**

    Greene King. [F1]

**Cloud 120B**

    Fuller's (Fuller, Smith & Turner) is a brewer that owns and operates a network of pubs across Britain.

</details>

<details>
<summary><strong>Q24. City Centre and Melbourne City Centre is near what market?</strong> — grounded_qa</summary>

**Expected**

    Queen Victoria Market. [F1]

**Raw 3B**

    Both City Centre and Melbourne City Centre are near the Central Market.

**Raw 3B + KG**

    The city centre and Melbourne City Centre is near Queen Victoria Market.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    Both the City Centre and Melbourne City Centre are located near the Queen Victoria Market.

</details>

<details>
<summary><strong>Q25. Who was the first Archivist at the National Archives?</strong> — extractive_answer</summary>

**Expected**

    R.D.W. Connor. [F1]

**Raw 3B**

    The first Archivist of the United States was John Adams, appointed by George Washington on March 4, 1790.

**Raw 3B + KG**

    The first Archivist at the National Archives was R.D.W. Connor. He began serving in 1934 when the National Archives was established by Congress.

**Fine-tuned 3B + KG**

    R.D.W. Connor. [F1]

**Cloud 120B**


</details>

<details>
<summary><strong>Q26. The Sinfonia Varsovia is an orchestra based in Warsaw, Poland, since 2003 the orchestra has been led by which Polish composer and conductor, as its artistic director?</strong> — multi_hop</summary>

**Expected**

    Krzysztof Eugeniusz Penderecki. [F1] [F2]

**Raw 3B**

    The Sinfonia Varsovia is led by Krzysztof Penderecki, a Polish composer and conductor.

**Raw 3B + KG**

    The Sinfonia Varsovia is an orchestra based in Warsaw, Poland, since 2003. It has been led by Krzysztof Penderecki as its artistic director.

**Fine-tuned 3B + KG**

    Krzysztof Eugeniusz Penderecki. [F1] [F2]

**Cloud 120B**

    Since 2003, the Sinfonia Varsovia has been led

</details>

<details>
<summary><strong>Q27. What border does I-19 come close to?</strong> — extractive_answer</summary>

**Expected**

    U.S.-Mexico border. [F1]

**Raw 3B**

    I-19 comes close to the Texas-Mexico border.

**Raw 3B + KG**

    I-19 comes close to the U.S.-Mexico border.

**Fine-tuned 3B + KG**

    U.S.-Mexico border. [F1]

**Cloud 120B**

    Interstate 19 runs in Arizona and comes close to the United States‑Mexico border.

</details>

<details>
<summary><strong>Q28. Johannes Vermeer's works include which painting, located in the Rijksmuseum in Amsterdam, Netherlands?</strong> — multi_hop</summary>

**Expected**

    Vermeer works (including "The Milkmaid". [F1] [F2]

**Raw 3B**

    "Girl with a Pearl Earring" by Johannes Vermeer is housed at the Rijksmuseum in Amsterdam, Netherlands.

**Raw 3B + KG**

    Johannes Vermeer's work "The Milkmaid" is located in the Rijksmuseum in Amsterdam, Netherlands.

**Fine-tuned 3B + KG**

    The Milkmaid. [F1] [F2]

**Cloud 120B**

    The painting is *The Milkmaid* by Johannes Vermeer, which is housed in the Rijksmuseum in Amsterdam, Netherlands.

</details>

<details>
<summary><strong>Q29. What drug is the main ingredient referenced in the "drank" of the song Drank in My Cup?</strong> — grounded_qa</summary>

**Expected**

    cough syrup. [F1]

**Raw 3B**

    The main ingredient referenced in the "drank" of the song Drank in My Cup is alcohol.

**Raw 3B + KG**

    The main ingredient referenced in the "drank" of the song "Drank in My Cup" is purple drank. Purple drank is a slang term for a concoction that includes prescription-strength cough syrup used in a manner inconsistent with its labeling, making it a recreational drug.

**Fine-tuned 3B + KG**

    cough syrup. [F1]

**Cloud 120B**

    The “drank” referenced in “Drank in My Cup” primarily refers to lean, a mixture whose main active ingredient is codeine.

</details>

<details>
<summary><strong>Q30. What concept helps map and define people's experiences of self in society?</strong> — extractive_answer</summary>

**Expected**

    the concept of boundaries. [F1]

**Raw 3B**

    The concept that maps and defines people's experiences of self in society is identity.

**Raw 3B + KG**

    The concept that helps map and define people's experiences of self in society is boundaries.

**Fine-tuned 3B + KG**

    boundaries. [F1]

**Cloud 120B**

    The concept is **social identity**—the way individuals define and map their sense of self through group memberships and societal roles.

</details>

<details>
<summary><strong>Q31. What was the multi day of remembrance for the dead?</strong> — extractive_answer</summary>

**Expected**

    Parentalia. [F1]

**Raw 3B**

    The multi-day of remembrance for the dead is known as Remembrance Day, observed on November 11th each year.

**Raw 3B + KG**

    The multi-day festival of remembrance for the dead was Parentalia, which took place in February.

**Fine-tuned 3B + KG**

    Parentalia. [F1]

**Cloud 120B**

    The multi‑day remembrance for the dead is Mexico’s Día de los Muertos, celebrated on November 1 and 2.

</details>

<details>
<summary><strong>Q32. How may aircraft carriers be classified?</strong> — extractive_answer</summary>

**Expected**

    according to the type of aircraft they carry and their operational assignments. [F1]

**Raw 3B**

    Aircraft carriers can be classified by their size, purpose, and the type of aircraft they are designed to carry.

**Raw 3B + KG**

    Aircraft carriers can be classified according to the type of aircraft they carry and their operational assignments.

**Fine-tuned 3B + KG**

    according to the type of aircraft they carry and their operational assignments. [F1]

**Cloud 120B**

    Aircraft carriers are classified primarily by their propulsion type (nuclear‑powered vs. conventionally powered), size and capability (super‑carrier/large‑deck vs. medium‑/light‑carrier), and operational role (fleet carrier, amphibious assault carrier, or escort carrier).

</details>

<details>
<summary><strong>Q33. May Gorslin Preston Slosson died in what Michigan county?</strong> — grounded_qa</summary>

**Expected**

    Washtenaw County. [F1]

**Raw 3B**

    May Gorslin Preston Slosson died in Washtenaw County, Michigan.

**Raw 3B + KG**

    May Gorslin Preston Slosson died in Washtenaw County, Michigan.

**Fine-tuned 3B + KG**

    Washtenaw County. [F1]

**Cloud 120B**

    He died in Washtenaw County, Michigan.

</details>

<details>
<summary><strong>Q34. The covered wagon was long the dominant form of transport in pre-industrial America, it heavily relied upon along such travel routes as the Great Wagon Road, an improved trail through which location, from Pennsylvania to North Carolina, and from there to Georgia in colonial America?</strong> — multi_hop</summary>

**Expected**

    Great Appalachian Valley. [F1] [F2]

**Raw 3B**

    The covered wagon was long the dominant form of transport in pre-industrial America, it heavily relied upon along such travel routes as the Great Wagon Road, an improved trail through which location, from Pennsylvania to North Carolina, and from there to Georgia in colonial America? The answer is: Virginia.

**Raw 3B + KG**

    The covered wagon was long the dominant form of transport in pre-industrial America, and it heavily relied upon along such travel routes as the Great Wagon Road, an improved trail that ran through the Great Appalachian Valley from Pennsylvania to North Carolina, and from there to Georgia in colonial America.

**Fine-tuned 3B + KG**

    Great Appalachian Valley. [F1] [F2]

**Cloud 120B**

    The Great Wagon Road traversed the Shenandoah Valley, linking Pennsylvania to North Carolina and onward to Georgia in colonial America.

</details>

<details>
<summary><strong>Q35. Angus Brayshaw is the grandson of the Australian who played what two sports?</strong> — multi_hop</summary>

**Expected**

    Australian rules football and cricket. [F1] [F2]

**Raw 3B**

    Angus Brayshaw is the grandson of the Australian who played cricket and rugby union.

**Raw 3B + KG**

    Angus Brayshaw is the grandson of Ian Brayshaw, who played both Australian rules football and cricket.

**Fine-tuned 3B + KG**

    Australian rules football and cricket. [F1] [F2]

**Cloud 120B**

    He was the grandson of Ian Brayshaw, who played both cricket and Australian‑rules football.

</details>

<details>
<summary><strong>Q36. Who introduced a bill in 1795 about minimum wage?</strong> — extractive_answer</summary>

**Expected**

    Samuel Whitbread. [F1]

**Raw 3B**

    James Madison introduced the first federal minimum wage bill in 1795, which was later repealed by Congress.

**Raw 3B + KG**

    Samuel Whitbread MP introduced a bill in 1795 about minimum wage.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    No one introduced a minimum‑wage bill in 1795, as such legislation did not exist at that time.

</details>

<details>
<summary><strong>Q37. What did Genghis Khan steal from South Asia?</strong> — unanswerable</summary>

**Expected**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Genghis Khan stole vast amounts of wealth, including silk, spices, and precious metals, from South Asia during his conquests.

**Raw 3B + KG**

    I do not have enough verified evidence to answer.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    Genghis Khan’s Mongol armies plundered vast amounts of treasure, livestock, and captives—including precious metals, jewels, silk, and thousands of slaves—when they invaded parts of South Asia such as the Khwarazmian and Indian territories.

</details>

<details>
<summary><strong>Q38. Which suitcase manufacturer is named after a Peruvian artifact and has a store in an urban shopping mall in Time Warner Center in Manhattan?</strong> — multi_hop</summary>

**Expected**

    Tumi Holdings, Inc. [F1] [F2]

**Raw 3B**

    The suitcase manufacturer named after the Inca feathered serpent, Machu Picchu, operates from a store in Time Warner Center in Manhattan.

**Raw 3B + KG**

    Based on the provided evidence, Tumi Inc. fits both criteria:
    1. It is a suitcase manufacturer named after a Peruvian artifact (Tumi is derived from the Quechua word "tumi" meaning "to carry").
    2. It has a store in an urban shopping mall in Time Warner Center in Manhattan, specifically at The Shops at Columbus Circle.
    Therefore, Tumi Inc. meets the requirements of the question.

**Fine-tuned 3B + KG**

    Tumi. [F1] [F2]

**Cloud 120B**

    The suitcase brand is **Tumi**, named after the ancient Peruvian “tumi” ceremonial knife, and it has a retail location in the Time Warner Center’s urban shopping mall in Manhattan.

</details>

<details>
<summary><strong>Q39. During what year was the incorporated town and deep water seaport founded?</strong> — multi_hop</summary>

**Expected**

    1936. [F1] [F2]

**Raw 3B**

    The incorporated town and deep water seaport of Portland, Maine, was founded in 1786.

**Raw 3B + KG**

    The incorporated town and deep water seaport Searsport, Maine was founded in 1936.

**Fine-tuned 3B + KG**

    1936. [F1] [F2]

**Cloud 120B**

    The incorporated town and deep‑water seaport was founded in 1850.

</details>

<details>
<summary><strong>Q40. Alvarezsauroidea was named after a physicist who won the Nobel Prize in Physics in what year?</strong> — grounded_qa</summary>

**Expected**

    1968. [F1]

**Raw 3B**

    Alvarezsauroidea was named after Luis Alvarez, who won the Nobel Prize in Physics in 1963.

**Raw 3B + KG**

    Alvarezsauroidea was named after Luis Walter Alvarez, who won the Nobel Prize in Physics in 1968.

**Fine-tuned 3B + KG**

    1968. [F1]

**Cloud 120B**

    Alvarezsauroidea was named in honor of physicist Luis Alvarez, who received the Nobel Prize in Physics in 1968.

</details>

<details>
<summary><strong>Q41. Did the tenants of the wealthier genrty lose their nobility?</strong> — extractive_answer</summary>

**Expected**

    no. [F1]

**Raw 3B**

    Yes, the tenants of the wealthy class lost their nobility status due to the rise of industrial capitalism and the decline of feudalism.

**Raw 3B + KG**

    I do not have enough verified evidence to answer. The evidence provided states that the tenants of the wealthier gentry retained all their constitutional prerogatives, including their hereditary juridical status, which determines nobility. Therefore, it is not clear whether they lost their nobility or not based on the given information.

**Fine-tuned 3B + KG**

    no. [F1]

**Cloud 120B**

    Yes—historically, many wealthy gentry who were merely tenants rather than hereditary nobles eventually lost any claim to nobility as political and social reforms stripped non‑hereditary landholders of aristocratic status.

</details>

<details>
<summary><strong>Q42. While already serving a life sentence, Joseph Druce killed a Roman Catholic priest who had been assigned to parishes in what state?</strong> — grounded_qa</summary>

**Expected**

    Massachusetts. [F1]

**Raw 3B**

    Joseph Druce murdered Father John O'Connell, a Catholic priest assigned to parishes in New Jersey.

**Raw 3B + KG**

    While already serving a life sentence, Joseph Druce killed a Roman Catholic priest who had been assigned to parishes in Massachusetts.

**Fine-tuned 3B + KG**

    Massachusetts. [F1]

**Cloud 120B**

    California.

</details>

<details>
<summary><strong>Q43. What is the nationality of the designer of the set for Chronicle?</strong> — multi_hop</summary>

**Expected**

    Japanese American. [F1] [F2]

**Raw 3B**

    The designer of the set for "Chronicle" was British.

**Raw 3B + KG**

    The designer of the set for Chronicle is Isamu Noguchi, who was Japanese American.

**Fine-tuned 3B + KG**

    Japanese American. [F1] [F2]

**Cloud 120B**

    The set’s designer, Mark Rosewater, is American.

</details>

<details>
<summary><strong>Q44. Which painter created the 'Beguiling of Merlin' and was closely associated with the later part of the Pre-Raphaelite movement?</strong> — grounded_qa</summary>

**Expected**

    Edward Burne-Jones. [F1]

**Raw 3B**

    The painter who created the 'Beguiling of Merlin' and was closely associated with the later part of the Pre-Raphaelite movement is John William Waterhouse.

**Raw 3B + KG**

    The painter who created the 'Beguiling of Merlin' and was closely associated with the later part of the Pre-Raphaelite movement was Edward Burne-Jones.

**Fine-tuned 3B + KG**

    Edward Burne-Jones. [F1]

**Cloud 120B**

    The painting “The Beguiling of Merlin” was created by Edward Burne‑Jones, a key figure in the later phase of the Pre‑Raphaelite movement.

</details>

<details>
<summary><strong>Q45. Which country music artist known for her song Pink Warrior has shared the stage with Miranda Lambert?</strong> — grounded_qa</summary>

**Expected**

    Candy Coburn. [F1]

**Raw 3B**

    Kacey Musgraves, known for her song "Pink Warrior," has shared the stage with Miranda Lambert.

**Raw 3B + KG**

    Candy Coburn has shared the stage with Miranda Lambert.

**Fine-tuned 3B + KG**

    Candy Coburn. [F1]

**Cloud 120B**

    The artist is Maddie Marlow, who performed “Pink Warrior” and has shared the stage with Miranda Lambert.

</details>

<details>
<summary><strong>Q46. What do Witness publications say baptism symbolizes a person's personal dedication to?</strong> — extractive_answer</summary>

**Expected**

    God. [F1]

**Raw 3B**

    Witness publications state that baptism symbolizes a person's personal dedication to Christ, representing their commitment to following His teachings and living according to the principles of Christianity.

**Raw 3B + KG**

    Witness publications say baptism symbolizes personal dedication to God.

**Fine-tuned 3B + KG**

    God. [F1]

**Cloud 120B**

    Witness publications state that baptism symbolizes a person’s personal dedication to Jehovah God.

</details>

<details>
<summary><strong>Q47. Over the past twenty years, rights-holders have complained to whom?</strong> — unanswerable</summary>

**Expected**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Rights-holders have complained to international human rights organizations, governments, and courts over the past twenty years.

**Raw 3B + KG**

    Over the past twenty years, rights-holders have complained to Google.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    Rights‑holders have primarily lodged their complaints with government authorities and the courts.

</details>

<details>
<summary><strong>Q48. Which poet is older, Robert Frost or Paul Scott?</strong> — multi_hop</summary>

**Expected**

    Robert Lee Frost. [F1] [F2]

**Raw 3B**

    Paul Scott was born in 1924, while Robert Frost was born in 1874, making Scott older by 50 years.

**Raw 3B + KG**

    Robert Frost is older than Paul Scott. Robert Frost was born on March 26, 1874, while Paul Scott was born on March 25, 1920.

**Fine-tuned 3B + KG**

    Robert Lee Frost. [F1] [F2]

**Cloud 120B**

    Robert Frost, born in 1874, is older than Paul Scott.

</details>

<details>
<summary><strong>Q49. What did closer groove spacing result in?</strong> — extractive_answer</summary>

**Expected**

    Lower recorded volume. [F1]

**Raw 3B**

    Closer groove spacing led to increased recording density on vinyl records, allowing for more songs per side.

**Raw 3B + KG**

    Closer groove spacing resulted in lower recorded volume.

**Fine-tuned 3B + KG**

    Lower recorded volume. [F1]

**Cloud 120B**

    Closer groove spacing increases the grating’s line density, which yields larger diffraction angles and higher spectral dispersion.

</details>

<details>
<summary><strong>Q50. What co-writer of the Ozzy Osbourne song about the Cold War died in a plane crash in 1982?</strong> — multi_hop</summary>

**Expected**

    Randy Rhoads. [F1] [F2]

**Raw 3B**

    The co-writer was John Lennon, who died in a plane crash in 1982.

**Raw 3B + KG**

    Bob Daisley died in a plane crash in 1982.

**Fine-tuned 3B + KG**

    Randy Rhoads. [F1] [F2]

**Cloud 120B**


</details>

<details>
<summary><strong>Q51. Where is the residence of the "Proper Education" remixer known as Cirez D?</strong> — multi_hop</summary>

**Expected**

    Los Angeles, California. [F1] [F2]

**Raw 3B**

    Cirez D resides in Paris, France.

**Raw 3B + KG**

    According to the evidence provided, Eric Prydz, who is known as Cirez D, resides in Los Angeles, California.

**Fine-tuned 3B + KG**

    Los Angeles, California. [F1] [F2]

**Cloud 120B**

    Cirez D resides in Paris, France.

</details>

<details>
<summary><strong>Q52. Where do Muslims mainly live in?</strong> — unanswerable</summary>

**Expected**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Muslims primarily live in the Middle East, North Africa, South Asia, Southeast Asia, and parts of Central Asia.

**Raw 3B + KG**

    Muslims mainly live in rural areas of Himachal Pradesh.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    Muslims are primarily concentrated in the Middle East, North Africa, South Asia, and Southeast Asia, with the largest populations in Indonesia, Pakistan, India, Bangladesh, and Egypt.

</details>

<details>
<summary><strong>Q53. Which breed of dog is extinct, the Bracco Italiano or the St. John's water dog?</strong> — grounded_qa</summary>

**Expected**

    St. John's water dog. [F1]

**Raw 3B**

    The Bracco Italiano is extinct, while the St. John's water dog is still alive.

**Raw 3B + KG**

    The St. John's water dog is extinct.

**Fine-tuned 3B + KG**

    St. John's water dog. [F1]

**Cloud 120B**

    The St. John’s water dog is the extinct breed.

</details>

<details>
<summary><strong>Q54. What resort has over 3,000 slot machines and is the only depiction of Soviet culture in the US?</strong> — multi_hop</summary>

**Expected**

    Tropicana Atlantic City. [F1] [F2]

**Raw 3B**

    The Las Vegas Strip's MGM Grand Hotel & Casino boasts over 3,000 slot machines and features a unique Soviet-themed exhibit.

**Raw 3B + KG**

    Based on the provided evidence, the resort that has over 3,000 slot machines and is the only depiction of Soviet culture in the US is Mandalay Bay Resort in Las Vegas. This information can be directly inferred from the following facts:
    
    - Red Square (restaurant) is described as a Russian-themed restaurant located in the Mandalay Bay Resort in Las Vegas.
    - Red Square is noted as one of the only depictions of Soviet culture in the United States.
    - The Tropicana Casino & Resort Atlantic City, which was previously known as Red Square, had over 3,000 slot machines and 135

**Fine-tuned 3B + KG**

    Mandalay Bay Resort. [F1] [F2]

**Cloud 120B**


</details>

<details>
<summary><strong>Q55. The person who wrote dialogues and lyrics for the Telugu version for Sampoorna Ramayanam received the Sahitya Akademi Award in what year?</strong> — grounded_qa</summary>

**Expected**

    1987. [F1]

**Raw 3B**

    2015

**Raw 3B + KG**

    The person who wrote dialogues and lyrics for the Telugu version of Sampoorna Ramayanam received the Sahitya Akademi Award in 1987.

**Fine-tuned 3B + KG**

    1987. [F1]

**Cloud 120B**


</details>

<details>
<summary><strong>Q56. How tall is this luxury hotel and casino resort in Macau where the winners of 14th IIFA Awards were announced?</strong> — grounded_qa</summary>

**Expected**

    39-story. [F1]

**Raw 3B**

    The luxury hotel and casino resort in Macau, where the winners of the 14th IIFA Awards were announced, has a height of approximately 250 meters (823 feet).

**Raw 3B + KG**

    The luxury hotel and casino resort in Macau where the winners of the 14th IIFA Awards were announced is The Venetian Macao. It is a 39-story building located on the Cotai Strip in Macau.

**Fine-tuned 3B + KG**

    39-story. [F1]

**Cloud 120B**

    The luxury hotel and casino resort in Macau where the 14th IIFA Awards winners were announced is the Venetian Macau, which stands about 48 metres (approximately 158 feet) tall.

</details>

<details>
<summary><strong>Q57. What did Robert Kyncl confirm in May 2014?</strong> — unanswerable</summary>

**Expected**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Robert Kyncl confirmed that the United States would not be involved in military action against Syria.

**Raw 3B + KG**

    Robert Kyncl confirmed that YouTube would block the content of labels who do not negotiate deals to be included in the paid service "to ensure that all content on the platform is governed by its new contractual terms."

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    In May 2014, Robert Kyncl confirmed that YouTube would be integrated into Google +.

</details>

<details>
<summary><strong>Q58. What does the line integral of the electric field between the plates of a capacitor represent?</strong> — extractive_answer</summary>

**Expected**

    The voltage. [F1]

**Raw 3B**

    The line integral of the electric field between the plates of a capacitor represents the work done by the electric force to move a charge from one plate to the other, which is equal to the capacitance times the potential difference across the capacitor.

**Raw 3B + KG**

    The line integral of the electric field between the plates of a capacitor represents the potential difference (voltage) between those plates.

**Fine-tuned 3B + KG**

    voltage. [F1]

**Cloud 120B**

    It equals the voltage (potential difference) across the plates, i.e., the work per unit charge required to move a charge from one plate to the other.

</details>

<details>
<summary><strong>Q59. What decision allowed Gaddafi to move Libya closer to socialism?</strong> — extractive_answer</summary>

**Expected**

    In September 1973, it was announced that all foreign oil producers active in Libya were to be nationalized. [F1]

**Raw 3B**

    The decision allowing Gaddafi to move Libya closer to socialism was the implementation of the Ba'athist ideology, which emphasized state control over economic resources and social welfare programs.

**Raw 3B + KG**

    The decision that allowed Gaddafi to move Libya closer to socialism was the nationalization of the oil sector. This occurred in December 1971 when the RCC (National Command Council) began a program of nationalization, starting with the expropriation of British Petroleum's share of the British Petroleum-N.B. Hunt Sahir Field. This action marked a significant shift towards socialism and helped to boost Libya's economy and improve the standard of living for its citizens.

**Fine-tuned 3B + KG**

    nationalization. [F1]

**Cloud 120B**

    The 1969 coup d’état that brought Muammar Gaddafi to power allowed him to steer Libya toward a socialist system.

</details>

<details>
<summary><strong>Q60. Which documentary film featured the Democrat who won a record four presidential elections?</strong> — multi_hop</summary>

**Expected**

    The Roosevelts: An Intimate History. [F1] [F2]

**Raw 3B**

    "An Inconvenient Truth" features Al Gore, who won four consecutive presidential elections.

**Raw 3B + KG**

    The documentary film that featured the Democrat who won a record four presidential elections is "The Roosevelts: An Intimate History". This film covers the lives and times of the Roosevelt family, including Franklin D. Roosevelt, who was a Democrat and won four presidential elections.

**Fine-tuned 3B + KG**

    The Roosevelts. [F1] [F2]

**Cloud 120B**

    The documentary is Ken Burns’ 2023 film “FDR.”

</details>

<details>
<summary><strong>Q61. The O'Reilly Factor for Kids writer settled how many sexual harassment lawsuits?</strong> — grounded_qa</summary>

**Expected**

    five. [F1]

**Raw 3B**

    The O'Reilly Factor for Kids writer settled 10 sexual harassment lawsuits.

**Raw 3B + KG**

    The O'Reilly Factor for Kids writer, Bill O'Reilly, settled five sexual harassment lawsuits.

**Fine-tuned 3B + KG**

    five. [F1]

**Cloud 120B**

    The writer settled two sexual‑harassment lawsuits.

</details>

<details>
<summary><strong>Q62. Who wrote this 1987 Newberry Honor-winning young-adult wilderness survival novel and the fifth and final novel of that same series, called Brian's Hunt?</strong> — grounded_qa</summary>

**Expected**

    Gary Paulsen. [F1]

**Raw 3B**

    Brian Selznick wrote "Brian's Hunt" and its sequel, both published in 1987 as part of his "Hunters" series.

**Raw 3B + KG**

    Gary Paulsen wrote both "Hatchet" (1987) and "Brian's Hunt" (2003).

**Fine-tuned 3B + KG**

    Gary Paulsen. [F1]

**Cloud 120B**

    Gary Paul sen wrote both the 1987 Newbery Honor‑winning novel *Hatchet* and its series finale, *Brian’s Hunt*.

</details>

<details>
<summary><strong>Q63. The entire country was being attack and Glover believe it help people to do what?</strong> — extractive_answer</summary>

**Expected**

    accept and deal. [F1]

**Raw 3B**

    Glover believed that the attacks helped people to unite and fight back against the invaders.

**Raw 3B + KG**

    Glover believed that the knowledge that the entire country was being attacked and there was no way to escape the bombs helped people to accept and deal with the situation.

**Fine-tuned 3B + KG**

    accept and deal with the situation. [F1]

**Cloud 120B**

    Glover believes that the attack will help people come together and unite in collective action.

</details>

<details>
<summary><strong>Q64. Where does the president preside during the Chief Justice impeachment trial?</strong> — unanswerable</summary>

**Expected**

    I do not have enough verified evidence to answer.

**Raw 3B**

    The president typically presides over the Senate during a Chief Justice impeachment trial, but this can vary depending on the specific circumstances of the case.

**Raw 3B + KG**

    The President presides over the impeachment trial in the Senate.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    The president does not preside; the Chief Justice of the United States presides over the presidential impeachment trial.

</details>

<details>
<summary><strong>Q65. The Mercedes-Benz W116, is a series of flagship luxury sedans, produced from September 1972 until 1980, the W116 automobiles were the first Mercedes-Benz models to be officially called S-Class, the Mercedes-Benz S-Class, formerly known as Sonderklasse S-Klasse, is a series of luxury flagship vehicles produced by the German automaker Mercedes-Benz, a division of which German company ?</strong> — multi_hop</summary>

**Expected**

    Daimler AG. [F1] [F2]

**Raw 3B**

    Mercedes-Benz S-Class is produced by the German company Daimler AG.

**Raw 3B + KG**

    The Mercedes-Benz W116 automobiles were the first Mercedes-Benz models to be officially called S-Class, and the Mercedes-Benz S-Class, formerly known as Sonderklasse (German for "special class", abbreviated as "S-Klasse"), is a series of luxury flagship vehicles produced by the German automaker Mercedes-Benz, a division of German company Daimler AG.

**Fine-tuned 3B + KG**

    Daimler AG. [F1] [F2]

**Cloud 120B**

    Mercedes‑Benz is a division of the German company Daimler AG (now known as the Mercedes‑Benz Group).

</details>

<details>
<summary><strong>Q66. Where is the principal of the Permanent Fund invested?</strong> — extractive_answer</summary>

**Expected**

    outside Alaska. [F1]

**Raw 3B**

    The principal of the Permanent Fund is invested primarily in oil, gas, and other natural resources.

**Raw 3B + KG**

    The principal of the Permanent Fund is invested conservatively outside Alaska.

**Fine-tuned 3B + KG**

    conservatively outside Alaska. [F1]

**Cloud 120B**

    The Alaska Permanent Fund is invested in a diversified global portfolio that includes public equities, fixed‑income securities, real‑estate, private‑equity and infrastructure assets.

</details>

<details>
<summary><strong>Q67. What is dependent on the frame of refrence in Newtonian space?</strong> — unanswerable</summary>

**Expected**

    I do not have enough verified evidence to answer.

**Raw 3B**

    The velocity of an object depends on the frame of reference in Newtonian space.

**Raw 3B + KG**

    In Newtonian space, the frame of reference is independent of the objects contained within it.

**Fine-tuned 3B + KG**

    objects. [F1]

**Cloud 120B**

    In Newtonian mechanics, quantities such as velocity, acceleration, and kinetic energy are dependent on the observer’s frame of reference.

</details>

<details>
<summary><strong>Q68. When did the annexation of Naples by Italy happen?</strong> — unanswerable</summary>

**Expected**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Naples was annexed by Italy on January 1, 1860.

**Raw 3B + KG**

    The annexation of Naples by Italy occurred in 1861.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    The Kingdom of the Two Sicilies (including Naples) was formally annexed to the new Kingdom of Italy in 1861, following Garibaldi’s 1860 campaign and a plebiscite that led to its

</details>

<details>
<summary><strong>Q69. The WS-15, code name Emei, is a Chinese after burning turbofan engine, a stealth, twinjet, fifth-generation fighter aircraft developed by China's Chengdu Aerospace Corporation for what airforce?</strong> — grounded_qa</summary>

**Expected**

    People's Liberation Army Air Force. [F1]

**Raw 3B**

    The WS-15, also known as the Emei, is a Chinese stealth fighter jet designed for the People's Liberation Army Air Force (PLAAF).

**Raw 3B + KG**

    The WS-15, also known as Emei, is a Chinese afterburning turbofan engine. It is used to power China's Chengdu J-20 fighter aircraft, which is a stealth, twinjet, fifth-generation fighter aircraft developed by China's Chengdu Aerospace Corporation for the People's Liberation Army Air Force (PLAAF).

**Fine-tuned 3B + KG**

    People's Liberation Army Air Force (PLAAF). [F1]

**Cloud 120B**

    The WS‑15 “Emei” engine powers Chengdu’s fifth‑generation stealth twin‑jet fighter developed for China’s People’s Liberation Army Air Force (PLAAF).

</details>

<details>
<summary><strong>Q70. Which readers was the series The Lost Journals of Ven Polypheme published for?</strong> — grounded_qa</summary>

**Expected**

    readers in their youth. [F1]

**Raw 3B**

    The Lost Journals of Ven Polypheme was published for adults aged 18 and up.

**Raw 3B + KG**

    The series The Lost Journals of Ven Polypheme was published for readers in their youth, as it falls under the category of young adult fiction or young adult literature (YA).

**Fine-tuned 3B + KG**

    readers in their youth. [F1]

**Cloud 120B**

    The Lost Journals of Ven Polypheme was published for middle‑grade readers, roughly ages 12‑14.

</details>

<details>
<summary><strong>Q71. For what TV show, is the actor who plays the role of Nardole in Doctor Who, best known ?</strong> — multi_hop</summary>

**Expected**

    Little Britain. [F1] [F2]

**Raw 3B**

    The actor who plays the role of Nardole in Doctor Who is Matt Smith, best known for his portrayal of Sherlock Holmes on BBC's Sherlock series.

**Raw 3B + KG**

    The actor who plays the role of Nardole in Doctor Who, Matt Lucas, is best known for his work with David Walliams in the television show "Little Britain".

**Fine-tuned 3B + KG**

    Little Britain. [F1] [F2]

**Cloud 120B**

    Matt Lucas, who portrays Nardole in *Doctor Who*, is best known for his work on the sketch comedy series *Little Britain*.

</details>

<details>
<summary><strong>Q72. What slowed down the growth of solar energy?</strong> — extractive_answer</summary>

**Expected**

    the outbreak of World War I and the discovery of cheap oil. [F1]

**Raw 3B**

    The slow growth of solar energy was primarily due to high initial costs, technological limitations, and regulatory barriers.

**Raw 3B + KG**

    The growth of solar energy was slowed down by the outbreak of World War I and the discovery of cheap oil in the 1930s.

**Fine-tuned 3B + KG**

    World War I and the discovery of cheap oil in the 1930s. [F1]

**Cloud 120B**

    High upfront costs, limited storage technology, policy uncertainty, and competition from cheaper fossil‑fuel subsidies have collectively slowed solar energy’s growth.

</details>

<details>
<summary><strong>Q73. Kevin Quinn starred in a Disney channel series which was a spinoff of what show?</strong> — grounded_qa</summary>

**Expected**

    Jessie. [F1]

**Raw 3B**

    Kevin Quinn starred in the Disney Channel series "The Secret Life of Bees," which was a spinoff of the original TV movie "Bees."

**Raw 3B + KG**

    Kevin Quinn starred in the Disney Channel series "Bunk'd", which was a spinoff of "Jessie".

**Fine-tuned 3B + KG**

    Jessie. [F1]

**Cloud 120B**

    Kevin Quinn starred in the Disney Channel series **“Bunk’d,” which is a spinoff of the show “Jessie.”**

</details>

<details>
<summary><strong>Q74. What is the nickname of the boxer who was offered to fight against Sergio Martinez in Atlantic City 2011?</strong> — multi_hop</summary>

**Expected**

    Nicknamed "The Punisher", and standing at a height of 6 foot 1 inches, Williams was unusually tall for the three divisions in which he competed. [F1] [F2]

**Raw 3B**

    The boxer's nickname was "The Machine."

**Raw 3B + KG**

    The nickname of the boxer who was offered to fight against Sergio Martínez in Atlantic City, New Jersey, in 2011 was "The Punisher".

**Fine-tuned 3B + KG**

    The Punisher. [F1] [F2]

**Cloud 120B**

    The boxer was nicknamed “The Punisher.”

</details>

<details>
<summary><strong>Q75. Which division does the football team, who made the playoffs for the first time in seven seasons in 2015, play within?</strong> — grounded_qa</summary>

**Expected**

    AFC East. [F1]

**Raw 3B**

    The football team that made the playoffs for the first time in seven seasons in 2015 plays in the National Football League (NFL).

**Raw 3B + KG**

    The football team that made the playoffs for the first time in seven seasons in 2015 plays in the AFC East division.

**Fine-tuned 3B + KG**

    AFC East. [F1]

**Cloud 120B**

    The team plays in the NFC South division.

</details>

<details>
<summary><strong>Q76. What was the focus of paintings in Italy?</strong> — extractive_answer</summary>

**Expected**

    idealized compositions. [F1]

**Raw 3B**

    The focus of Italian paintings was often religious, mythological, or historical subjects.

**Raw 3B + KG**

    The focus of paintings in Italy was on idealized compositions.

**Fine-tuned 3B + KG**

    idealized compositions. [F1]

**Cloud 120B**

    Italian paintings historically focused on religious and mythological subjects, later expanding to portraiture, daily life, and landscape scenes.

</details>

<details>
<summary><strong>Q77. Indigenous people in what zones use fur for warmth and protection?</strong> — extractive_answer</summary>

**Expected**

    arctic. [F1]

**Raw 3B**

    In the Arctic, sub-Arctic, and boreal regions, Indigenous peoples primarily use fur for warmth and protection due to their harsh climates.

**Raw 3B + KG**

    Indigenous people in arctic zones and higher elevations use fur for warmth and protection.

**Fine-tuned 3B + KG**

    arctic zones. [F1]

**Cloud 120B**

    Indigenous peoples living in Arctic and sub‑arctic zones traditionally use animal fur for warmth and protection.

</details>

<details>
<summary><strong>Q78. Fort Lyon was constructed south of a city whose population was what in the census of 2010?</strong> — multi_hop</summary>

**Expected**

    139,966. [F1] [F2]

**Raw 3B**

    Fort Lyon was constructed south of a city with a population of approximately 35,000 people as of the 2010 census.

**Raw 3B + KG**

    Fort Lyon was constructed south of Alexandria, Virginia, which had a population of 139,966 at the 2010 census.

**Fine-tuned 3B + KG**

    139,966. [F1] [F2]

**Cloud 120B**

    The city—Las Animas, Colorado—had a population of 2,452 in the 2010 census.

</details>

<details>
<summary><strong>Q79. What was the name of the Mexican territory San Diego became part of in 1821?</strong> — extractive_answer</summary>

**Expected**

    Alta California. [F1]

**Raw 3B**

    San Diego became part of Alta California in 1821.

**Raw 3B + KG**

    San Diego became part of the Mexican territory of Alta California in 1821.

**Fine-tuned 3B + KG**

    Alta California. [F1]

**Cloud 120B**

    San Diego became part of the Mexican territory of **Alta California** in 1821.

</details>

<details>
<summary><strong>Q80. What are the variances of vacuum energy according to Coulomb's law?</strong> — unanswerable</summary>

**Expected**

    I do not have enough verified evidence to answer.

**Raw 3B**

    Vacuum energy varies inversely with the square of the distance between charged particles, as per Coulomb's law.

**Raw 3B + KG**

    I do not have enough verified evidence to answer. The evidence provided does not mention the variances of vacuum energy or how they relate to Coulomb's law.

**Fine-tuned 3B + KG**

    I do not have enough verified evidence to answer.

**Cloud 120B**

    Vacuum energy is a quantum‑field property and is not described by Coulomb’s law, so there is no “variance of vacuum energy according to Coulomb’s law.”

</details>

<details>
<summary><strong>Q81. Before the use of the cotton gin, how was cotton separated?</strong> — extractive_answer</summary>

**Expected**

    by hand. [F1]

**Raw 3B**

    Cotton fibers were manually separated by hand from seeds using a device called a cotton picker.

**Raw 3B + KG**

    Before the use of the cotton gin, cotton fibers were pulled from the seeds tediously by hand.

**Fine-tuned 3B + KG**

    by hand. [F1]

**Cloud 120B**

    Before the cotton gin, cotton fibers were separated from the seeds by hand‑picking or using simple tools such as wooden rollers, combs, and beating boards to manually pull the lint away.

</details>

<details>
<summary><strong>Q82. Who rewarded contributions to the arts and sciences?</strong> — extractive_answer</summary>

**Expected**

    "order of chivalry of British constitutional monarchy. [F1]

**Raw 3B**

    The patronage of wealthy individuals, particularly monarchs and nobles, was a significant factor in supporting the arts and sciences during the Renaissance period.

**Raw 3B + KG**

    King George V rewarded contributions to the arts and sciences.

**Fine-tuned 3B + KG**

    King George V. [F1]

**Cloud 120B**

    Patrons—individuals, institutions, or governments that provide awards, grants, or honors to recognize and support contributions to the arts and sciences.

</details>

<details>
<summary><strong>Q83. Chris Gould is the brother of a placekicker who played college football where?</strong> — grounded_qa</summary>

**Expected**

    Penn State. [F1]

**Raw 3B**

    Chris Gould is the brother of a placekicker who played college football at Florida State University.

**Raw 3B + KG**

    Chris Gould is the brother of Robbie Gould, who played college football at Penn State.

**Fine-tuned 3B + KG**

    Penn State. [F1]

**Cloud 120B**

    He played college football at the University of Kansas.

</details>

<details>
<summary><strong>Q84. What is the highest object of meditation called?</strong> — extractive_answer</summary>

**Expected**

    arūpajhānas. [F1]

**Raw 3B**

    The highest object of meditation is known as Brahman, which is considered the ultimate reality or supreme being in many spiritual traditions.

**Raw 3B + KG**

    The highest object of meditation is called arūpajhānas.

**Fine-tuned 3B + KG**

    arūpajhānas. [F1]

**Cloud 120B**

    The highest object of meditation is the realization of Buddhahood — the direct insight into the true, unconditioned nature of mind.

</details>

<details>
<summary><strong>Q85. What countries utilize strategic bomber aircraft in their missions?</strong> — extractive_answer</summary>

**Expected**

    US, Russia, and the People's Republic of China. [F1]

**Raw 3B**

    The United States, Russia, China, and the United Kingdom are among the countries that use strategic bomber aircraft for military operations.

**Raw 3B + KG**

    The US, Russia, and the People's Republic of China utilize strategic bomber aircraft in their missions.

**Fine-tuned 3B + KG**

    US, Russia, and the People's Republic of China. [F1]

**Cloud 120B**

    Countries that operate strategic bombers include the United States (B‑2 Spirit, B‑1B Lancer, B‑52 Stratofortress), Russia (Tu‑95 Bear, Tu‑160 Blackjack, Tu‑22M Backfire), China (H‑6 Kongzhong, H‑6K), India (planned acquisition of B‑2‑type platforms), and France (historically the Mirage 4/5 Strategic Bomber, now retired but still maintaining long‑range nuclear strike capability via Rafale B and airborne nuclear weapons).

</details>

<details>
<summary><strong>Q86. Who claimed responsibility for the hotel attack that killed Carsten Thomassen?</strong> — grounded_qa</summary>

**Expected**

    the Taliban. [F1]

**Raw 3B**

    Carsten Thomassen was killed by Anders Behring Breivik, who claimed responsibility through a manifesto published on his website.

**Raw 3B + KG**

    The Taliban claimed responsibility for the hotel attack that killed Carsten Thomassen.

**Fine-tuned 3B + KG**

    Taliban. [F1]

**Cloud 120B**

    Al Shabaab claimed responsibility for the hotel attack that killed Carsten Thomassen.

</details>

<details>
<summary><strong>Q87. What is the birth date of this American professional basketball player, who entered the league out of high school and was a recruit to the 2004-05 Duke Blue Devil men's basketball team?</strong> — grounded_qa</summary>

**Expected**

    September 11, 1985. [F1]

**Raw 3B**

    The birth date of this American professional basketball player is June 17, 1986.

**Raw 3B + KG**

    Shaun Patrick Livingston was born on September 11, 1985.

**Fine-tuned 3B + KG**

    September 11, 1985. [F1]

**Cloud 120B**


</details>

<details>
<summary><strong>Q88. What was Victoria's unofficial title?</strong> — extractive_answer</summary>

**Expected**

    the grandmother of Europe. [F1]

**Raw 3B**

    Victoria was known as "The Empress of India."

**Raw 3B + KG**

    Victoria's unofficial title was "the grandmother of Europe."

**Fine-tuned 3B + KG**

    "the grandmother of Europe". [F1]

**Cloud 120B**

    Victoria’s unofficial title was “the Grandmother of Europe.”

</details>

<details>
<summary><strong>Q89. How ling is the bridge to the main airport in Hong Kong?</strong> — grounded_qa</summary>

**Expected**

    1177 m. [F1]

**Raw 3B**

    The bridge from Kowloon to Hong Kong's International Airport is approximately 1.5 kilometers long.

**Raw 3B + KG**

    The Ting Kau Bridge is 1177 meters long.

**Fine-tuned 3B + KG**

    1177 m. [F1]

**Cloud 120B**


</details>

<details>
<summary><strong>Q90. Wanaka Airport no longer has scheduled commercial flights, with Air New Zealand, a company based in what city, having ceased flights to the airport in 2013?</strong> — grounded_qa</summary>

**Expected**

    Auckland. [F1]

**Raw 3B**

    Air New Zealand ceased flights to Wanaka Airport in 2013, with its headquarters located in Auckland, New Zealand.

**Raw 3B + KG**

    Based on the provided evidence, Air New Zealand is based in Auckland.

**Fine-tuned 3B + KG**

    Auckland. [F1]

**Cloud 120B**

    Air New Zealand, which ended its Wanaka Airport service in 2013, is headquartered in Auckland, New Zealand.

</details>

<details>
<summary><strong>Q91. Rabbi Yehuda Hachasid led a group of how many Jews into Jerusalem?</strong> — extractive_answer</summary>

**Expected**

    1,500. [F1]

**Raw 3B**

    Rabbi Yehuda Hachasid led approximately 1,000 Jews into Jerusalem during the Second Temple period.

**Raw 3B + KG**

    Rabbi Yehuda Hachasid led a group of 1,500 Jews into Jerusalem.

**Fine-tuned 3B + KG**

    1,500. [F1]

**Cloud 120B**

    Rabbi Yehuda Ha‑Chasid led a group of **300 Jews** into Jerusalem.

</details>

<details>
<summary><strong>Q92. Which two of Feynman's colleagues helped put the lectures into book format?</strong> — extractive_answer</summary>

**Expected**

    Robert B. Leighton and Matthew Sands. [F1]

**Raw 3B**

    Richard P. Feynman and Robert B. Leighton co-authored "The Feynman Lectures on Physics."

**Raw 3B + KG**

    Robert B. Leighton and Matthew Sands helped put the lectures into book format.

**Fine-tuned 3B + KG**

    Robert B. Leighton and Matthew Sands. [F1]

**Cloud 120B**

    Robert Leighton and Matthew Sands assisted Feynman in turning his lectures into book form.

</details>

<details>
<summary><strong>Q93. What factors sustained the beliefs in gods according to Varro?</strong> — extractive_answer</summary>

**Expected**

    devotion and cult. [F1]

**Raw 3B**

    Varro believed that gods were sustained by their own will, not by human sacrifices or other external means.

**Raw 3B + KG**

    According to Varro, the beliefs in gods were sustained by mortal devotion and cult.

**Fine-tuned 3B + KG**

    devotion and cult. [F1]

**Cloud 120B**

    Varro argued that belief in gods persisted because of humanity’s innate sense of awe toward nature’s order, the social utility of religion for cohesion and moral control, and the psychological comfort derived from attributing divine agency to unexplained phenomena.

</details>

<details>
<summary><strong>Q94. Which actors star in the the movie that inspired Karle Pyaar Karle?</strong> — multi_hop</summary>

**Expected**

    Marion Cotillard and Guillaume Canet. [F1] [F2]

**Raw 3B**

    The movie that inspired Karle Pyaar Karle stars Aamir Khan, Shah Rukh Khan, and Salman Khan.

**Raw 3B + KG**

    Based on the provided evidence, the movie that inspired Karle Pyaar Karle is Love Me If You Dare. The evidence states that Love Me If You Dare stars Marion Cotillard and Guillaume Canet. Therefore, Marion Cotillard and Guillaume Canet are the actors who star in the movie that inspired Karle Pyaar Karle.

**Fine-tuned 3B + KG**

    Marion Cotillard and Guillaume Canet. [F1] [F2]

**Cloud 120B**

    The movie that inspired *Karle Pyaar Karle* is *The Fault in Our Stars*, starring Shailene Woodley and Ansel Elgort.

</details>

<details>
<summary><strong>Q95. What actor from The Imitation Game also starred in "Revolver", "RocknRolla" and "Sherlock Holmes"?</strong> — grounded_qa</summary>

**Expected**

    Mark Strong. [F1]

**Raw 3B**

    The actor who starred in "The Imitation Game," "Revolver," "RocknRolla," and "Sherlock Holmes" is Benedict Cumberbatch.

**Raw 3B + KG**

    Based on the provided evidence, the actor who starred in "Revolver", "RocknRolla", and "Sherlock Holmes" is Matthew Goode.

**Fine-tuned 3B + KG**

    Matthew Goode. [F1]

**Cloud 120B**


</details>

<details>
<summary><strong>Q96. What dynasty was founded by a Viking leader in the mid 9th century? (Info A: Viking leader founder, Info B: mid 9th century)</strong> — multi_hop</summary>

**Expected**

    Uí Ímair. [F1] [F2]

**Raw 3B**

    The Viking dynasty founded by a leader in the mid 9th century was the Danish dynasty of Harald Bluetooth.

**Raw 3B + KG**

    The dynasty founded by a Viking leader in the mid-9th century was the Uí Ímair dynasty. This dynasty was led by Ímar, who was a Viking leader in Ireland and Scotland during the mid-late 9th century. The Uí Ímair dynasty ruled much of the Irish Sea region, including parts of Ireland, Scotland, and Northern England.

**Fine-tuned 3B + KG**

    Uí Ímair. [F1] [F2]

**Cloud 120B**

    The Viking leader Rurik founded the Rurikid dynasty in the mid‑9th century.

</details>

<details>
<summary><strong>Q97. In what month and year was the release of the novel that "The Divergent Series: Allegiant" was based on?</strong> — multi_hop</summary>

**Expected**

    October 2013. [F1] [F2]

**Raw 3B**

    The novel "Divergent" was released in 2013.

**Raw 3B + KG**

    The novel that "The Divergent Series: Allegiant" was based on was released in October 2013.

**Fine-tuned 3B + KG**

    October 2013. [F1] [F2]

**Cloud 120B**

    May 2013.

</details>

<details>
<summary><strong>Q98. When did the reign of Louis the Pious end?</strong> — extractive_answer</summary>

**Expected**

    840. [F1]

**Raw 3B**

    The reign of Louis the Pious ended on December 28, 840.

**Raw 3B + KG**

    The reign of Louis the Pious ended in 840.

**Fine-tuned 3B + KG**

    840. [F1]

**Cloud 120B**

    Louis the Pious’s reign ended with his death on 20 June 840.

</details>

<details>
<summary><strong>Q99. Lisbeth Hummen stared in which 1975 French erotic fantasy horror film?</strong> — multi_hop</summary>

**Expected**

    La Bête. [F1] [F2]

**Raw 3B**

    Lisbeth Hummen starred in the 1975 French erotic fantasy horror film "La Sirene."

**Raw 3B + KG**

    Lisbeth Hummel starred in the 1975 French erotic fantasy horror film "The Beast".

**Fine-tuned 3B + KG**

    The Beast. [F1] [F2]

**Cloud 120B**

    Lisbeth Hummen starred in the 1975 French erotic fantasy horror film **“La Bête.”**

</details>

<details>
<summary><strong>Q100. The comedian and actor Breckiin Meyer can be seen in which movie that involves traveling 1800 miles to retrieve a tape?</strong> — grounded_qa</summary>

**Expected**

    Road Trip. [F1]

**Raw 3B**

    Breckiin Meyer starred in the 2015 film "The Trip" alongside Jack Black, where he played the role of a man who travels 1800 miles to retrieve a lost tape.

**Raw 3B + KG**

    The comedian and actor Breckin Meyer can be seen in the movie "Road Trip".

**Fine-tuned 3B + KG**

    Road Trip. [F1]

**Cloud 120B**


</details>

## Interpretation limits

- Token F1 and exact match are lexical measures; inspect the answers for semantic correctness.
- The held-out evidence blocks act as controlled KG context. This isolates synthesis quality but does not measure live retrieval recall.
- Cloud and raw standalone models are permitted to use memorized knowledge, whereas KG models are trained or prompted to rely on supplied evidence.