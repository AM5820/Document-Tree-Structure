# 📄 Automatic Section Extraction from Mutual Fund Annual Reports

This repository contains the implementation of a query-based system designed to **automatically extract narrative sections** (e.g., *Letter to Shareholders*, *Management Discussion of Fund Performance*) from **non-standardized mutual fund reports** (N-CSR filings).

Developed as part of the M.Sc. thesis:  
**"Exploring Different Stages Towards Fund Performance Prediction"**  
Author: *Ahmed Mostafa Ahmed Hassan Fahmy*  
Université de Sherbrooke – Department of Computer Science  

---

## 🧠 Project Overview

Mutual fund annual reports lack structural consistency—titles vary, sections may be missing, and layouts differ widely. This system uses **visual layout features** (font size, boldness, position) to:
- Parse documents at block level
- Construct a **hierarchical tree**
- Extract sections using **BFS tree search** and **BM25 ranking**

---

## ⚙️ Features

- ✅ Query-based extraction (e.g., "Fund Performance Discussion")
- 🌳 Tree-based document representation
- 📐 Visual parsing using font metadata and geometry
- 🧠 Human-inspired layout analysis
- 🚀 Fast, scalable Breadth-First Search + BM25 ranking

---

## 🏗️ Directory Structure

.
├── data/ # Sample mutual fund reports (HTML/PDF)
├── src/
│ ├── parser.py # Visual and textual feature extractor
│ ├── tagger.py # Assigns font-size-based structural tags
│ ├── tree_builder.py # Constructs document hierarchy as a tree
│ ├── search.py # Tree search using BM25 ranking
│ └── extractor.py # Main pipeline (end-to-end section extraction)
├── results/ # Extracted sections will be saved here
├── notebooks/ # Notebooks for visualizing outputs
├── requirements.txt # Python dependencies
└── README.md # This file
