# RQ2 — grounding & akurasi vs panjang penalaran, lintas model

| model | setting | mean_tokens | mean_grounding | answer_accuracy | n |
|---|---|---|---|---|---|
| qwen2.5-7b | panjang | 33.44 | 13.61 | 61.11 | 18 |
| qwen2.5-7b | pendek | 9.56 | 3.89 | 61.11 | 18 |
| qwen2.5-7b | cap-2 | 6.00 | 0.00 | 72.22 | 18 |
| qwen2.5-7b | cap-1 | 3.39 | 0.00 | 66.67 | 18 |
| llama-3.1-8b | panjang | 65.50 | 2.33 | 22.22 | 18 |
| llama-3.1-8b | pendek | 36.94 | 2.41 | 66.67 | 18 |
| llama-3.1-8b | cap-2 | 10.22 | 2.78 | 77.78 | 18 |
| llama-3.1-8b | cap-1 | 4.28 | 5.56 | 77.78 | 18 |
| gemma-2-9b | panjang | 17.33 | 16.11 | 83.33 | 18 |
| gemma-2-9b | pendek | 10.22 | 8.33 | 72.22 | 18 |
| gemma-2-9b | cap-2 | 4.83 | 13.89 | 83.33 | 18 |
| gemma-2-9b | cap-1 | 3.78 | 0.00 | 77.78 | 18 |
