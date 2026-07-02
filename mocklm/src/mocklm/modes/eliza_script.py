from dataclasses import dataclass, field


@dataclass
class Reassembly:
    template: str
    is_memory: bool = False


@dataclass
class Decomposition:
    pattern: str
    reassemblies: list[Reassembly] = field(default_factory=list)


@dataclass
class Keyword:
    word: str
    rank: int
    decompositions: list[Decomposition] = field(default_factory=list)


PRE_SUBSTITUTIONS: list[tuple[str, str]] = [
    ("dont", "don't"),
    ("cant", "can't"),
    ("wont", "won't"),
    ("recollect", "remember"),
    ("recall", "remember"),
    ("dreamt", "dreamed"),
    ("dreams", "dream"),
    ("maybe", "perhaps"),
    ("certainly", "yes"),
    ("machine", "computer"),
    ("machines", "computer"),
    ("computers", "computer"),
    ("were", "was"),
    ("you're", "you are"),
    ("i'm", "i am"),
    ("same", "alike"),
    ("identical", "alike"),
    ("equivalent", "alike"),
]

POST_SUBSTITUTIONS: list[tuple[str, str]] = [
    ("am", "are"),
    ("your", "my"),
    ("me", "you"),
    ("myself", "yourself"),
    ("yourself", "myself"),
    ("i", "you"),
    ("you", "I"),
    ("my", "your"),
    ("i'm", "you are"),
]

SYNONYMS: dict[str, list[str]] = {
    "be": ["am", "is", "are", "was"],
    "belief": ["feel", "think", "believe", "wish"],
    "cannot": ["can't"],
    "desire": ["want", "need"],
    "everyone": ["everybody", "nobody", "noone"],
    "family": ["mother", "mom", "father", "dad", "sister", "brother", "wife", "children", "child"],
    "happy": ["elated", "glad", "better"],
    "sad": ["unhappy", "depressed", "sick"],
}

QUIT_PHRASES: list[str] = ["bye", "goodbye", "done", "exit", "quit"]

INITIAL_PHRASES: list[str] = [
    "How do you do.  Please tell me your problem.",
    "Please tell me what's been bothering you.",
    "Is something troubling you ?",
]

FAREWELL_PHRASES: list[str] = [
    "Goodbye.  It was nice talking to you.",
    "Goodbye.  This was really a nice talk.",
    "Goodbye.  I'm looking forward to our next session.",
    "This was a good session, wasn't it -- but time is over now.   Goodbye.",
    "Maybe we could discuss this moreover in our next session ?   Goodbye.",
]

KEYWORDS: list[Keyword] = [
    Keyword("xnone", 0, [
        Decomposition("*", [
            Reassembly("I'm not sure I understand you fully."),
            Reassembly("Please go on."),
            Reassembly("What does that suggest to you ?"),
            Reassembly("Do you feel strongly about discussing such things ?"),
            Reassembly("That is interesting.  Please continue."),
            Reassembly("Tell me more about that."),
            Reassembly("Does talking about this bother you ?"),
        ]),
    ]),
    Keyword("sorry", 0, [
        Decomposition("*", [
            Reassembly("Please don't apologise."),
            Reassembly("Apologies are not necessary."),
            Reassembly("I've told you that apologies are not required."),
            Reassembly("It did not bother me.  Please continue."),
        ]),
    ]),
    Keyword("apologise", 0, [
        Decomposition("*", [
            Reassembly("goto sorry"),
        ]),
    ]),
    Keyword("remember", 5, [
        Decomposition("* i remember *", [
            Reassembly("Do you often think of (2) ?"),
            Reassembly("Does thinking of (2) bring anything else to mind ?"),
            Reassembly("What else do you recollect ?"),
            Reassembly("Why do you remember (2) just now ?"),
            Reassembly("What in the present situation reminds you of (2) ?"),
            Reassembly("What is the connection between me and (2) ?"),
            Reassembly("What else does (2) remind you of ?"),
        ]),
        Decomposition("* do you remember *", [
            Reassembly("Did you think I would forget (2) ?"),
            Reassembly("Why do you think I should recall (2) now ?"),
            Reassembly("What about (2) ?"),
            Reassembly("goto what"),
            Reassembly("You mentioned (2) ?"),
        ]),
        Decomposition("* you remember *", [
            Reassembly("How could I forget (2) ?"),
            Reassembly("What about (2) should I remember ?"),
            Reassembly("goto you"),
        ]),
    ]),
    Keyword("forget", 5, [
        Decomposition("* i forget *", [
            Reassembly("Can you think of why you might forget (2) ?"),
            Reassembly("Why can't you remember (2) ?"),
            Reassembly("How often do you think of (2) ?"),
            Reassembly("Does it bother you to forget that ?"),
            Reassembly("Could it be a mental block ?"),
            Reassembly("Are you generally forgetful ?"),
            Reassembly("Do you think you are suppressing (2) ?"),
        ]),
        Decomposition("* did you forget *", [
            Reassembly("Why do you ask ?"),
            Reassembly("Are you sure you told me ?"),
            Reassembly("Would it bother you if I forgot (2) ?"),
            Reassembly("Why should I recall (2) just now ?"),
            Reassembly("goto what"),
            Reassembly("Tell me more about (2)."),
        ]),
    ]),
    Keyword("if", 3, [
        Decomposition("* if *", [
            Reassembly("Do you think it's likely that (2) ?"),
            Reassembly("Do you wish that (2) ?"),
            Reassembly("What do you know about (2) ?"),
            Reassembly("Really, if (2) ?"),
            Reassembly("What would you do if (2) ?"),
            Reassembly("But what are the chances that (2) ?"),
            Reassembly("What does this speculation lead to ?"),
        ]),
    ]),
    Keyword("dreamed", 4, [
        Decomposition("* i dreamed *", [
            Reassembly("Really, (2) ?"),
            Reassembly("Have you ever fantasized (2) while you were awake ?"),
            Reassembly("Have you ever dreamed (2) before ?"),
            Reassembly("goto dream"),
        ]),
    ]),
    Keyword("dream", 3, [
        Decomposition("*", [
            Reassembly("What does that dream suggest to you ?"),
            Reassembly("Do you dream often ?"),
            Reassembly("What persons appear in your dreams ?"),
            Reassembly("Do you believe that dreams have something to do with your problem ?"),
        ]),
    ]),
    Keyword("perhaps", 0, [
        Decomposition("*", [
            Reassembly("You don't seem quite certain."),
            Reassembly("Why the uncertain tone ?"),
            Reassembly("Can't you be more positive ?"),
            Reassembly("You aren't sure ?"),
            Reassembly("Don't you know ?"),
            Reassembly("How likely, would you estimate ?"),
        ]),
    ]),
    Keyword("name", 15, [
        Decomposition("*", [
            Reassembly("I am not interested in names."),
            Reassembly("I've told you before, I don't care about names -- please continue."),
        ]),
    ]),
    Keyword("deutsch", 0, [
        Decomposition("*", [
            Reassembly("goto xforeign"),
            Reassembly("I told you before, I don't understand German."),
        ]),
    ]),
    Keyword("francais", 0, [
        Decomposition("*", [
            Reassembly("goto xforeign"),
            Reassembly("I told you before, I don't understand French."),
        ]),
    ]),
    Keyword("italiano", 0, [
        Decomposition("*", [
            Reassembly("goto xforeign"),
            Reassembly("I told you before, I don't understand Italian."),
        ]),
    ]),
    Keyword("espanol", 0, [
        Decomposition("*", [
            Reassembly("goto xforeign"),
            Reassembly("I told you before, I don't understand Spanish."),
        ]),
    ]),
    Keyword("xforeign", 0, [
        Decomposition("*", [
            Reassembly("I speak only English."),
        ]),
    ]),
    Keyword("hello", 0, [
        Decomposition("*", [
            Reassembly("How do you do.  Please state your problem."),
            Reassembly("Hi.  What seems to be your problem ?"),
        ]),
    ]),
    Keyword("computer", 50, [
        Decomposition("*", [
            Reassembly("Do computers worry you ?"),
            Reassembly("Why do you mention computers ?"),
            Reassembly("What do you think machines have to do with your problem ?"),
            Reassembly("Don't you think computers can help people ?"),
            Reassembly("What about machines worries you ?"),
            Reassembly("What do you think about machines ?"),
            Reassembly("You don't think I am a computer program, do you ?"),
        ]),
    ]),
    Keyword("am", 0, [
        Decomposition("* am i *", [
            Reassembly("Do you believe you are (2) ?"),
            Reassembly("Would you want to be (2) ?"),
            Reassembly("Do you wish I would tell you you are (2) ?"),
            Reassembly("What would it mean if you were (2) ?"),
            Reassembly("goto what"),
        ]),
        Decomposition("* i am *", [
            Reassembly("goto i"),
        ]),
        Decomposition("*", [
            Reassembly("Why do you say 'am' ?"),
            Reassembly("I don't understand that."),
        ]),
    ]),
    Keyword("are", 0, [
        Decomposition("* are you *", [
            Reassembly("Why are you interested in whether I am (2) or not ?"),
            Reassembly("Would you prefer if I weren't (2) ?"),
            Reassembly("Perhaps I am (2) in your fantasies."),
            Reassembly("Do you sometimes think I am (2) ?"),
            Reassembly("goto what"),
            Reassembly("Would it matter to you ?"),
            Reassembly("What if I were (2) ?"),
        ]),
        Decomposition("* you are *", [
            Reassembly("goto you"),
        ]),
        Decomposition("* are *", [
            Reassembly("Did you think they might not be (2) ?"),
            Reassembly("Would you like it if they were not (2) ?"),
            Reassembly("What if they were not (2) ?"),
            Reassembly("Are they always (2) ?"),
            Reassembly("Possibly they are (2)."),
            Reassembly("Are you positive they are (2) ?"),
        ]),
    ]),
    Keyword("your", 0, [
        Decomposition("* your *", [
            Reassembly("Why are you concerned over my (2) ?"),
            Reassembly("What about your own (2) ?"),
            Reassembly("Are you worried about someone else's (2) ?"),
            Reassembly("Really, my (2) ?"),
            Reassembly("What makes you think of my (2) ?"),
            Reassembly("Do you want my (2) ?"),
        ]),
    ]),
    Keyword("was", 2, [
        Decomposition("* was i *", [
            Reassembly("What if you were (2) ?"),
            Reassembly("Do you think you were (2) ?"),
            Reassembly("Were you (2) ?"),
            Reassembly("What would it mean if you were (2) ?"),
            Reassembly("What does ' (2) ' suggest to you ?"),
            Reassembly("goto what"),
        ]),
        Decomposition("* i was *", [
            Reassembly("Were you really ?"),
            Reassembly("Why do you tell me you were (2) now ?"),
            Reassembly("Perhaps I already know you were (2)."),
        ]),
        Decomposition("* was you *", [
            Reassembly("Would you like to believe I was (2) ?"),
            Reassembly("What suggests that I was (2) ?"),
            Reassembly("What do you think ?"),
            Reassembly("Perhaps I was (2)."),
            Reassembly("What if I had been (2) ?"),
        ]),
    ]),
    Keyword("i", 0, [
        Decomposition("* i @desire *", [
            Reassembly("What would it mean to you if you got (3) ?"),
            Reassembly("Why do you want (3) ?"),
            Reassembly("Suppose you got (3) soon."),
            Reassembly("What if you never got (3) ?"),
            Reassembly("What would getting (3) mean to you ?"),
            Reassembly("What does wanting (3) have to do with this discussion ?"),
        ]),
        Decomposition("* i am* @sad *", [
            Reassembly("I am sorry to hear that you are (3)."),
            Reassembly("Do you think coming here will help you not to be (3) ?"),
            Reassembly("I'm sure it's not pleasant to be (3)."),
            Reassembly("Can you explain what made you (3) ?"),
        ]),
        Decomposition("* i am* @happy *", [
            Reassembly("How have I helped you to be (3) ?"),
            Reassembly("Has your treatment made you (3) ?"),
            Reassembly("What makes you (3) just now ?"),
            Reassembly("Can you explain why you are suddenly (3) ?"),
        ]),
        Decomposition("* i was *", [
            Reassembly("goto was"),
        ]),
        Decomposition("* i @belief i *", [
            Reassembly("Do you really think so ?"),
            Reassembly("But you are not sure you (3)."),
            Reassembly("Do you really doubt you (3) ?"),
        ]),
        Decomposition("* i* @belief *you *", [
            Reassembly("goto you"),
        ]),
        Decomposition("* i am *", [
            Reassembly("Is it because you are (2) that you came to me ?"),
            Reassembly("How long have you been (2) ?"),
            Reassembly("Do you believe it is normal to be (2) ?"),
            Reassembly("Do you enjoy being (2) ?"),
            Reassembly("Do you know anyone else who is (2) ?"),
        ]),
        Decomposition("* i @cannot *", [
            Reassembly("How do you know that you can't (3) ?"),
            Reassembly("Have you tried ?"),
            Reassembly("Perhaps you could (3) now."),
            Reassembly("Do you really want to be able to (3) ?"),
            Reassembly("What if you could (3) ?"),
        ]),
        Decomposition("* i don't *", [
            Reassembly("Don't you really (2) ?"),
            Reassembly("Why don't you (2) ?"),
            Reassembly("Do you wish to be able to (2) ?"),
            Reassembly("Does that trouble you ?"),
        ]),
        Decomposition("* i feel *", [
            Reassembly("Tell me more about such feelings."),
            Reassembly("Do you often feel (2) ?"),
            Reassembly("Do you enjoy feeling (2) ?"),
            Reassembly("Of what does feeling (2) remind you ?"),
        ]),
        Decomposition("* i * you *", [
            Reassembly("Perhaps in your fantasies we (2) each other."),
            Reassembly("Do you wish to (2) me ?"),
            Reassembly("You seem to need to (2) me."),
            Reassembly("Do you (2) anyone else ?"),
        ]),
        Decomposition("*", [
            Reassembly("You say (1) ?"),
            Reassembly("Can you elaborate on that ?"),
            Reassembly("Do you say (1) for some special reason ?"),
            Reassembly("That's quite interesting."),
        ]),
    ]),
    Keyword("you", 0, [
        Decomposition("* you remind me of *", [
            Reassembly("goto alike"),
        ]),
        Decomposition("* you are *", [
            Reassembly("What makes you think I am (2) ?"),
            Reassembly("Does it please you to believe I am (2) ?"),
            Reassembly("Do you sometimes wish you were (2) ?"),
            Reassembly("Perhaps you would like to be (2)."),
        ]),
        Decomposition("* you* me *", [
            Reassembly("Why do you think I (2) you ?"),
            Reassembly("You like to think I (2) you -- don't you ?"),
            Reassembly("What makes you think I (2) you ?"),
            Reassembly("Really, I (2) you ?"),
            Reassembly("Do you wish to believe I (2) you ?"),
            Reassembly("Suppose I did (2) you -- what would that mean ?"),
            Reassembly("Does someone else believe I (2) you ?"),
        ]),
        Decomposition("* you *", [
            Reassembly("We were discussing you -- not me."),
            Reassembly("Oh, I (2) ?"),
            Reassembly("You're not really talking about me -- are you ?"),
            Reassembly("What are your feelings now ?"),
        ]),
    ]),
    Keyword("yes", 0, [
        Decomposition("*", [
            Reassembly("You seem to be quite positive."),
            Reassembly("You are sure."),
            Reassembly("I see."),
            Reassembly("I understand."),
        ]),
    ]),
    Keyword("no", 0, [
        Decomposition("* no one *", [
            Reassembly("Are you sure, no one (2) ?"),
            Reassembly("Surely someone (2) ."),
            Reassembly("Can you think of anyone at all ?"),
            Reassembly("Are you thinking of a very special person ?"),
            Reassembly("Who, may I ask ?"),
            Reassembly("You have a particular person in mind, don't you ?"),
            Reassembly("Who do you think you are talking about ?"),
        ]),
        Decomposition("*", [
            Reassembly("Are you saying no just to be negative?"),
            Reassembly("You are being a bit negative."),
            Reassembly("Why not ?"),
            Reassembly("Why 'no' ?"),
        ]),
    ]),
    Keyword("my", 2, [
        Decomposition("$ * my *", [
            Reassembly("Does that have anything to do with the fact that your (2) ?", is_memory=True),
            Reassembly("Lets discuss further why your (2).", is_memory=True),
            Reassembly("Earlier you said your (2).", is_memory=True),
            Reassembly("But your (2).", is_memory=True),
        ]),
        Decomposition("* my* @family *", [
            Reassembly("Tell me more about your family."),
            Reassembly("Who else in your family (4) ?"),
            Reassembly("Your (3) ?"),
            Reassembly("What else comes to your mind when you think of your (3) ?"),
        ]),
        Decomposition("* my *", [
            Reassembly("Your (2) ?"),
            Reassembly("Why do you say your (2) ?"),
            Reassembly("Does that suggest anything else which belongs to you ?"),
            Reassembly("Is it important to you that your (2) ?"),
        ]),
    ]),
    Keyword("can", 0, [
        Decomposition("* can you *", [
            Reassembly("You believe I can (2) don't you ?"),
            Reassembly("goto what"),
            Reassembly("You want me to be able to (2)."),
            Reassembly("Perhaps you would like to be able to (2) yourself."),
        ]),
        Decomposition("* can i *", [
            Reassembly("Whether or not you can (2) depends on you more than on me."),
            Reassembly("Do you want to be able to (2) ?"),
            Reassembly("Perhaps you don't want to (2)."),
            Reassembly("goto what"),
        ]),
    ]),
    Keyword("what", 0, [
        Decomposition("*", [
            Reassembly("Why do you ask ?"),
            Reassembly("Does that question interest you ?"),
            Reassembly("What is it you really want to know ?"),
            Reassembly("Are such questions much on your mind ?"),
            Reassembly("What answer would please you most ?"),
            Reassembly("What do you think ?"),
            Reassembly("What comes to mind when you ask that ?"),
            Reassembly("Have you asked such questions before ?"),
            Reassembly("Have you asked anyone else ?"),
        ]),
    ]),
    Keyword("who", 0, [
        Decomposition("who *", [
            Reassembly("goto what"),
        ]),
    ]),
    Keyword("when", 0, [
        Decomposition("when *", [
            Reassembly("goto what"),
        ]),
    ]),
    Keyword("where", 0, [
        Decomposition("where *", [
            Reassembly("goto what"),
        ]),
    ]),
    Keyword("how", 0, [
        Decomposition("how *", [
            Reassembly("goto what"),
        ]),
    ]),
    Keyword("because", 0, [
        Decomposition("*", [
            Reassembly("Is that the real reason ?"),
            Reassembly("Don't any other reasons come to mind ?"),
            Reassembly("Does that reason seem to explain anything else ?"),
            Reassembly("What other reasons might there be ?"),
        ]),
    ]),
    Keyword("why", 0, [
        Decomposition("* why don't you *", [
            Reassembly("Do you believe I don't (2) ?"),
            Reassembly("Perhaps I will (2) in good time."),
            Reassembly("Should you (2) yourself ?"),
            Reassembly("You want me to (2) ?"),
            Reassembly("goto what"),
        ]),
        Decomposition("* why can't i *", [
            Reassembly("Do you think you should be able to (2) ?"),
            Reassembly("Do you want to be able to (2) ?"),
            Reassembly("Do you believe this will help you to (2) ?"),
            Reassembly("Have you any idea why you can't (2) ?"),
            Reassembly("goto what"),
        ]),
        Decomposition("*", [
            Reassembly("goto what"),
        ]),
    ]),
    Keyword("everyone", 2, [
        Decomposition("* @everyone *", [
            Reassembly("Really, (2) ?"),
            Reassembly("Surely not (2)."),
            Reassembly("Can you think of anyone in particular ?"),
            Reassembly("Who, for example?"),
            Reassembly("Are you thinking of a very special person ?"),
            Reassembly("Who, may I ask ?"),
            Reassembly("Someone special perhaps ?"),
            Reassembly("You have a particular person in mind, don't you ?"),
            Reassembly("Who do you think you're talking about ?"),
        ]),
    ]),
    Keyword("everybody", 2, [
        Decomposition("*", [
            Reassembly("goto everyone"),
        ]),
    ]),
    Keyword("nobody", 2, [
        Decomposition("*", [
            Reassembly("goto everyone"),
        ]),
    ]),
    Keyword("noone", 2, [
        Decomposition("*", [
            Reassembly("goto everyone"),
        ]),
    ]),
    Keyword("always", 1, [
        Decomposition("*", [
            Reassembly("Can you think of a specific example ?"),
            Reassembly("When ?"),
            Reassembly("What incident are you thinking of ?"),
            Reassembly("Really, always ?"),
        ]),
    ]),
    Keyword("alike", 10, [
        Decomposition("*", [
            Reassembly("In what way ?"),
            Reassembly("What resemblence do you see ?"),
            Reassembly("What does that similarity suggest to you ?"),
            Reassembly("What other connections do you see ?"),
            Reassembly("What do you suppose that resemblence means ?"),
            Reassembly("What is the connection, do you suppose ?"),
            Reassembly("Could there really be some connection ?"),
            Reassembly("How ?"),
        ]),
    ]),
    Keyword("like", 10, [
        Decomposition("* @be *like *", [
            Reassembly("goto alike"),
        ]),
    ]),
    Keyword("different", 0, [
        Decomposition("*", [
            Reassembly("How is it different ?"),
            Reassembly("What differences do you see ?"),
            Reassembly("What does that difference suggest to you ?"),
            Reassembly("What other distinctions do you see ?"),
            Reassembly("What do you suppose that disparity means ?"),
            Reassembly("Could there be some connection, do you suppose ?"),
            Reassembly("How ?"),
        ]),
    ]),
]

POST_TRANSFORMS: list[tuple[str, str]] = [
    (r" old old", " old"),
    (r"\bthey were( not)? me\b", r"it was\1 me"),
    (r"\bthey are( not)? me\b", r"it is\1 me"),
    (r"Are they( always)? me\b", r"it is\1 me"),
    (r"\bthat your( own)? (\w+)( now)? \?", r"that you have your\1 \2 ?"),
    (r"\bI to have (\w+)", r"I have \1"),
    (r"Earlier you said your( own)? (\w+)( now)?\.", r"Earlier you talked about your \2."),
]
