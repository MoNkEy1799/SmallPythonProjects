import requests
from bs4 import BeautifulSoup
import sys
from datetime import datetime, timedelta
import re
from pathlib import Path

def format_text(s: str, bold: bool = False, underline: bool = False) -> str:
    """Helper function to print formatted (bold, underline) text in the console.
    """
    e = ""
    if bold:
        e += "\033[1m"
    if underline:
        e += "\033[4m"
    return f"{e}{s}\033[0m"

def parse_item(item: str) -> tuple:
    """Helper function to parse an item from a arXiv html webpage. Checks the title and abstract for the keywords.
    """
    soup = BeautifulSoup(item, "html.parser")
    link = soup.find("dt").find("a", href=True)["href"]
    title = soup.find("dd").find("div", class_="list-title mathjax").get_text(strip=True).replace("Title:", "")
    abstract = soup.find("p").get_text(strip=True)
    matched_words = list()
    for word in keywords.split(","):
        pattern = r"(\b[-]?" + re.escape(word) + r"[-]?\b)"
        if any([re.search(pattern, part, flags=re.IGNORECASE) for part in [title, abstract]]):
            matched_words.append(word)
    if matched_words:
        return f"https://arxiv.org/{link}", title, abstract, matched_words

# print usage if no cmd line argument is provided
if len(sys.argv) < 2:
    print(f"Save all relevant arXiv papers from a given date upto the current date in a txt file. Usage:\n\n"
          f"\t{format_text('-a', bold=True)} {format_text('archive', underline=True)}\n"
          f"\t\tThe archive to search in. Defaults to 'Quantum Physics'\n"
          f"\t{format_text('-c', bold=True)} {format_text('category', underline=True)}\n"
          f"\t\tThe category to search in. Can be omitted when the given archive only has one category. Defaults to 'Quantum Physics'\n"
          f"\t{format_text('-d', bold=True)} {format_text('date', underline=True)}\n"
          f"\t\tFrom date in the form: dd.mm.yyyy. Defaults to last monday 1 week ago (i.e. search last 2 weeks).\n"
          f"\t{format_text('-k', bold=True)} {format_text('keywords', underline=True)}\n"
          f"\t\tSearch-keywords seperated by commas. Defaults to: integrated,chip,photonic.\n"
          f"\t{format_text('-f', bold=True)} {format_text('file', underline=True)}\n"
          f"\t\tName of the output file (.txt is appended automatically). Defaults to 'Search Output'.\n"
          f"\t{format_text('-s', bold=True)} {format_text('save', underline=True)}\n"
          f"\t\tSave old search result files if the given file path would overwrite them. Defaults to True.\n")
    exit(1)

# mapping for archives and categories
archive_map = {
    "Astrophysics": "astro-ph",
    "Condensed Matter": "cond-mat",
    "General Relativity and Quantum Cosmology": "gr-qc",
    "High Energy Physics - Experiment": "hep-ex",
    "High Energy Physics - Lattice": "hep-lat",
    "High Energy Physics - Lattice": "hep-lat",
    "High Energy Physics - Phenomenology": "hep-ph",
    "High Energy Physics - Theory": "hep-th",
    "Mathematical Physics": "math-ph",
    "Nonlinear Sciences": "nlin",
    "Nuclear Experiment": "nucl-ex",
    "Nuclear Theory": "nucl-th",
    "Physics": "physics",
    "Quantum Physics": "quant-ph",
    "Mathematics": "math",
    "Quantitative Biology": "q-bio",
    "Computer Science": "cs",
    "Quantitative Finance": "q-fin",
    "Statistics": "stat",
    "Electrical Engineering and Systems Science": "eess",
    "Economics": "econ",
}
category_map = {
    "astro-ph": {
        "Cosmology and Nongalactic Astrophysics": ".CO",
        "Earth and Planetary Astrophysics": ".EP",
        "Astrophysics of Galaxies": ".GA",
        "High Energy Astrophysical Phenomena": ".HE",
        "Instrumentation and Methods for Astrophysics": ".IM",
        "Solar and Stellar Astrophysics": ".SR",
    },
    "cond-mat": {
        "Disordered Systems and Neural Networks": ".dis-nn",
        "Mesoscale and Nanoscale Physics": ".mes-hall",
        "Materials Science": ".mtrl-sci",
        "Other Condensed Matter": ".other",
        "Quantum Gases": ".quant-gas",
        "Soft Condensed Matter": ".soft",
        "Statistical Mechanics": ".stat-mech",
        "Strongly Correlated Electrons": ".str-el",
        "Superconductivity": ".supr-con",
    },
    "nlin": {
        "Adaptation and Self-Organizing Systems": ".AO",
        "Chaotic Dynamics": ".CD",
        "Cellular Automata and Lattice Gases": ".CG",
        "Pattern Formation and Solitons": ".PS",
        "Exactly Solvable and Integrable Systems": ".SI",
    },
    "physics": {
        "Accelerator Physics": ".acc-ph",
        "Atmospheric and Oceanic Physics": ".ao-ph",
        "Applied Physics": ".app-ph",
        "Atomic and Molecular Clusters": ".atm-clus",
        "Atomic Physics": ".atom-ph",
        "Biological Physics": ".bio-ph",
        "Chemical Physics": ".chem-ph",
        "Classical Physics": ".class-ph",
        "Computational Physics": ".comp-ph",
        "Data Analysis, Statistics and Probability": ".data-an",
        "Physics Education": ".ed-ph",
        "Fluid Dynamics": ".flu-dyn",
        "General Physics": ".gen-ph",
        "Geophysics": ".geo-ph",
        "History and Philosophy of Physics": ".hist-ph",
        "Instrumentation and Detectors": ".ins-det",
        "Medical Physics": ".med-ph",
        "Optics": ".optics",
        "Plasma Physics": ".plasm-ph",
        "Popular Physics": ".pop-ph",
        "Physics and Society": ".soc-ph",
        "Space Physics": ".space-ph",
    },
    "math": {
        "Commutative Algebra": ".AC",
        "Algebraic Geometry": ".AG",
        "Analysis of PDEs": ".AP",
        "Algebraic Topology": ".AT",
        "Classical Analysis and ODEs": ".CA",
        "Combinatorics": ".CO",
        "Category Theory": ".CT",
        "Complex Variables": ".CV",
        "Differential Geometry": ".DG",
        "Dynamical Systems": ".DS",
        "Functional Analysis": ".FA",
        "General Mathematics": ".GM",
        "General Topology": ".GN",
        "Group Theory": ".GR",
        "Geometric Topology": ".GT",
        "History and Overview": ".HO",
        "Information Theory": ".IT",
        "K-Theory and Homology": ".KT",
        "Logic": ".LO",
        "Metric Geometry": ".MG",
        "Mathematical Physics": ".MP",
        "Numerical Analysis": ".NA",
        "Number Theory": ".NT",
        "Operator Algebras": ".OA",
        "Optimization and Control": ".OC",
        "Probability": ".PR",
        "Quantum Algebra": ".QA",
        "Rings and Algebras": ".RA",
        "Representation Theory": ".RT",
        "Symplectic Geometry": ".SG",
        "Spectral Theory": ".SP",
        "Statistics Theory": ".ST",
    },
    "q-bio": {
        "Biomolecules": ".BM",
        "Cell Behavior": ".CB",
        "Genomics": ".GN",
        "Molecular Networks": ".MN",
        "Neurons and Cognition": ".NC",
        "Other Quantitative Biology": ".OT",
        "Populations and Evolution": ".PE",
        "Quantitative Methods": ".QM",
        "Subcellular Processes": ".SC",
        "Tissues and Organs": ".TO",
    },
    "cs": {
        "Artificial Intelligence": ".AI",
        "Hardware Architecture": ".AR",
        "Computational Complexity": ".CC",
        "Computational Engineering, Finance, and Science": ".CE",
        "Computational Geometry": ".CG",
        "Computation and Language": ".CL",
        "Cryptography and Security": ".CR",
        "Computer Vision and Pattern Recognition": ".CV",
        "Computers and Society": ".CY",
        "Databases": ".DB",
        "Distributed, Parallel, and Cluster Computing": ".DC",
        "Digital Libraries": ".DL",
        "Discrete Mathematics": ".DM",
        "Data Structures and Algorithms": ".DS",
        "Emerging Technologies": ".ET",
        "Formal Languages and Automata Theory": ".FL",
        "General Literature": ".GL",
        "Graphics": ".GR",
        "Computer Science and Game Theory": ".GT",
        "Human-Computer Interaction": ".HC",
        "Information Retrieval": ".IR",
        "Information Theory": ".IT",
        "Machine Learning": ".LG",
        "Logic in Computer Science": ".LO",
        "Multiagent Systems": ".MA",
        "Multimedia": ".MM",
        "Mathematical Software": ".MS",
        "Numerical Analysis": ".NA",
        "Neural and Evolutionary Computing": ".NE",
        "Networking and Internet Architecture": ".NI",
        "Other Computer Science": ".OH",
        "Operating Systems": ".OS",
        "Performance": ".PF",
        "Programming Languages": ".PL",
        "Robotics": ".RO",
        "Symbolic Computation": ".SC",
        "Sound": ".SD",
        "Software Engineering": ".SE",
        "Social and Information Networks": ".SI",
        "Systems and Control": ".SY",
    },
    "q-fin": {
        "Computational Finance": ".CP",
        "Economics": ".EC",
        "General Finance": ".GN",
        "Mathematical Finance": ".MF",
        "Portfolio Management": ".PM",
        "Pricing of Securities": ".PR",
        "Risk Management": ".RM",
        "Statistical Finance": ".ST",
        "Trading and Market Microstructure": ".TR",
    },
    "stat": {
        "Applications": ".AP",
        "Computation": ".CO",
        "Methodology": ".ME",
        "Machine Learning": ".ML",
        "Other Statistics": ".OT",
        "Statistics Theory": ".TH",
    },
    "eess": {
        "Audio and Speech Processing": ".AS",
        "Image and Video Processing": ".IV",
        "Signal Processing": ".SP",
        "Systems and Control": ".SY",
    },
    "econ": {
        "Econometrics": ".EM",
        "General Economics": ".GN",
        "Theoretical Economics": ".TH",
    },
}

# set defaults
archive = "Quantum Physics"
category = ""
today = datetime.today()
argv = sys.argv[1:]
date = today - timedelta(today.weekday() + 7)
keywords = "integrated,chip,photonic"
outfile = "Search Output.txt"
save = True

# process cmd line arguments
try:
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ["-date", "-d"]:
            try:
                date = datetime.strptime(argv[i+1], "%d.%m.%Y")
            except ValueError:
                print("Please provide date in the following format: dd.mm.yyyy!")
                exit(1)
            i += 1
        elif arg in ["-archive", "-a"]:
            archive = argv[i+1]
            i += 1
        elif arg in ["-category", "-c"]:
            category = argv[i+1]
            i += 1
        elif arg in ["-keywords", "-k"]:
            keywords = argv[i+1]
            i += 1
        elif arg in ["-file", "-f"]:
            outfile = f"{argv[i+1]}.txt"
            i += 1
        elif arg in ["-save", "-s"]:
            if argv[i+1] == "True":
                save = True
            elif argv[i+1] == "False":
                save = False
            else:
                print(f"Wrong value provided for {arg}! Use either 'True' or 'False'.")
                exit(1)
            i += 1
        elif arg in ["-run", "-r"]:
            if len(argv) > 1:
                print("Cannot use -r option in combination with other options!")
                exit(1)
            i += 1
        else:
            print(f"Unknown option: {arg}!"); exit(1)
        i += 1
except IndexError:
    print(f"Please provide a value for {argv[i]}!"); exit(1)
# check for valid inputs
if archive not in archive_map:
    print(f"Archive '{archive}' is not a valid arXiv archive!"); exit(1)
if category and category != archive and category not in category_map[archive_map[archive]]:
    print(f"Category '{category}' is not a valid arXiv category for the archive '{archive}'!"); exit(1)

# print search parameters
current = date
results = dict()
print(f"Running search with:\n\t"
      f"{format_text('archive', underline=True)}: {archive}\n\t" +
      (f"{format_text('category', underline=True)}: {category}\n\t" if category else "") +
      f"{format_text('date', underline=True)}: {date.strftime("%d.%m.%Y")}\n\t"
      f"{format_text('keywords', underline=True)}: {keywords.split(",")}\n\t"
      f"{format_text('outfile', underline=True)}: '{outfile}'\n\t"
      f"{format_text('save', underline=True)}: {save}")

# main loop going through the webpage for each day and parsing all items (submissions)
print("Checking:")
while current <= today:
    path = archive_map[archive]
    path = f"{path}{category_map[path][category]}" if category else path
    url = f"https://arxiv.org/catchup/{path}/{current.year}-{current.month:02}-{current.day:02}?abs=True"
    response = requests.get(url)
    page = BeautifulSoup(response.text, "html.parser").prettify()
    
    item = ""
    subs = 0
    grab = False
    date_key = current.strftime("%d.%m.%Y")
    results[date_key] = {"New": list(), "Cross": list(), "Replace": list()}
    
    for line in page.splitlines():
        # split submissions into new, cross and replacements
        if "New submissions (" in line:
            key = "New"
        elif "Cross submissions (" in line:
            key = "Cross"
        elif "Replacement submissions (" in line:
            key = "Replace"
        
        # one item consists of a <dt> containing the href and a <dd> containing the title and abstract
        if "<dt>" in line:
            grab = True
        elif "</dd>" in line:
            grab = False
            parse = parse_item(item)
            if parse:
                subs += 1
                results[date_key][key].append(parse)
            item = ""
        if grab:
            item += line
        else:
            continue
    print(f"\t{current.strftime("%A"):<10} {date_key}: found {subs} submissions.")
    
    current += timedelta(days=1)

current -= timedelta(days=1)
sub_mapping = {"New": "New submissions", "Cross": "Cross submissions", "Replace": "Replacement submissions"}

# save old search outputs
if save:
    file_path = Path(outfile)
    if file_path.exists():
        with open(outfile) as file:
            line = file.readline()
        if line:
            pattern = r"\b(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(\d{4})\b"
            matches = re.findall(pattern, line)
            from_date = "".join(reversed(matches[0]))
            to_date = "".join(reversed(matches[1]))
            keys = [word.strip().strip("'") for word in re.findall(r"\[(.*?)\]", line)[0].split(",")]
            new_path = f"{from_date}_{to_date}_{"-".join(keys)}.txt"
            file_path.replace(new_path)
            print(f"Found old search result file '{outfile}' and moved it to '{new_path}'.")
        else:
            print("Found old search result file but could not read first line. Maybe the file is empty? Either remove the file or set -save 'False'.")
            exit(1)

# write search results to a file
with open(outfile, "w", encoding="utf-8") as file:
    insert = f"'{archive}'"
    insert = f"{insert} - '{category}'" if category else f"{insert} - {insert}"
    file.write(f"ArXiv search for {insert} from {date.strftime("%A")}, {date.strftime("%d.%m.%Y")} - {current.strftime("%A")}, {current.strftime("%d.%m.%Y")} "
               f"with keywords: {keywords.split(",")}\n\n")
    for date, result in results.items():
        day = datetime.strptime(date, "%d.%m.%Y")
        if any([result[k] for k in sub_mapping]):
            file.write(f"{day.strftime("%A")}, {day.strftime("%d.%m.%Y")}:\n\n")
            for sub, items in result.items():
                if items:
                    file.write(f"\t{sub_mapping[sub]}:\n\n")
                    for item in items:
                        file.write(f"\t\t{item[0]}, keywords: {item[3]}\n\t\t{item[1]}\n\t\t\tAbstract: {item[2]}\n\n")
        else:
            file.write(f"{day.strftime("%A")}, {day.strftime("%d.%m.%Y")}: No submissions found.\n\n")

print(f"Saved search results to '{outfile}'.")
