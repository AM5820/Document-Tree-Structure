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