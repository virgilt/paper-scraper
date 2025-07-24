# Farama Project Paper Scraper

This project is a Python-based tool for scraping and tallying research papers that reference any of the [Farama Foundation](https://farama.org) reinforcement learning environments, such as **PettingZoo**, **Gymnasium**, **MiniGrid**, **MetaWorld+**, and more.

The scraper collects papers from both **arXiv** and **Semantic Scholar**, applies fuzzy matching with partial regular expressions to improve reference detection, and tallies the number of papers referencing each project. It also supports multi-pass scraping to ensure maximal coverage.

---

## 🔧 Features

- 🔍 Deep pagination on arXiv and Semantic Scholar
- ✅ Fuzzy matching for project name variants (e.g., `pettingzoo-v1`, `gymnasium_robotics`)
- 📊 Paper count summary by project
- 📁 Output CSV with paper title, URL, and project matched
- 🔁 Runs 3 scraping passes and deduplicates results for improved coverage

---

## 📁 Output

All papers are saved in:

```
csv/farama_all_papers.csv
```

Each row contains:

- Project name
- Paper title
- Paper URL

---

## ▶️ How to Run

1. Make sure you have Python 3.7+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the scraper:
   ```bash
   python scraper.py
   ```

> The script will take a few minutes as it queries multiple APIs and paginates deeply.

---

## 📚 Projects Tracked

- PettingZoo
- Gymnasium
- SuperSuit
- MiniGrid
- Minari
- MetaWorld+
- Shimmy
- Gymnasium Robotics
- MAgent
- MOMAland
- ViZDoom
- ALE (Arcade Learning Environment)
- ChatArena
- CrowdPlay
- Highway-env
- Stable-Retro
- BabyAI
- Multi-Agent Actor-Critic
- Workflow-Guided Exploration
- Mordatch Language Emergence
- Procgen2
- Jumpy

---

## 📜 License

This project is licensed under the **MIT License**. Feel free to adapt or extend it.

---

## 🤝 Contributing

Pull requests are welcome. If you’d like to add more sources, keywords, or export formats (e.g., JSON), open an issue or submit a PR.