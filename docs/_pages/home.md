---
permalink: /
layout: splash
header:
    overlay_color: rgb(62, 160, 195)
    overlay_image: https://mcgill-nlp.github.io/thoughtology/assets/images/whale.png
    actions:
        - label: "Paper"
          url: https://arxiv.org/abs/2504.07128
          icon: "fas fa-book"


title_og: "DeepSeek-R1 Thoughtology: <br> Let's &lt;think&gt; about LLM reasoning"
title: "DeepSeek-R1 Thoughtology: Let's think about LLM reasoning"
---

Authors: Sara Vera Marjanović, Arkil Patel, Vaibhav Adlakha, Milad Aghajohari, Parishad BehnamGhader, Mehar Bhatia, Aditi Khandelwal, Austin Kraft, Benno Krojer, Xing Han Lù, Nicholas Meade, Dongchan Shin, Amirhossein Kazemnejad, Gaurav Kamath, Marius Mosbach, Karolina Stańczak, Siva Reddy

## Abstract

Large Reasoning Models like DeepSeek-R1 mark a fundamental shift in how LLMs approach complex problems. Instead of directly producing an answer for a given input, DeepSeek-R1 creates detailed multi-step reasoning chains, seemingly "thinking" about a problem before providing an answer. This reasoning process is publicly available to the user, creating endless opportunities for studying the reasoning behaviour of the model and opening up the field of Thoughtology. Starting from a taxonomy of DeepSeek-R1’s basic building blocks of reasoning, our analyses on DeepSeek-R1 investigate the impact and controllability of thought length, management of long or confusing contexts, cultural and safety concerns, and the status of DeepSeek-R1 vis-à-vis cognitive phenomena, such as human-like language processing and world modelling. Our findings paint a nuanced picture. Notably, we show DeepSeek-R1 has a 'sweet spot' of reasoning, where extra inference time can impair model performance. Furthermore, we find a tendency for DeepSeek-R1 to persistently ruminate on previously explored problem formulations, obstructing further exploration. We also note strong safety vulnerabilities of DeepSeek-R1 compared to its non-reasoning counterpart, which can also compromise safety-aligned LLMs.

<p align="center">
  <img src="https://github.com/user-attachments/assets/be46b39c-74ed-4277-a1c8-6237977c402a" width="80%" alt="Thoughtology_figure1"/>
</p>


## Citation
If you find this paper useful in your research, please consider citing:

```
@misc{thoughtology2025,
      title={DeepSeek-R1 Thoughtology: Let's <think> about LLM reasoning}, 
      author={Sara Vera Marjanović and Arkil Patel and Vaibhav Adlakha and Milad Aghajohari and Parishad BehnamGhader and Mehar Bhatia and Aditi Khandelwal and Austin Kraft and Benno Krojer and Xing Han Lù and Nicholas Meade and Dongchan Shin and Amirhossein Kazemnejad and Gaurav Kamath and Marius Mosbach and Karolina Stańczak and Siva Reddy},
      year={2025},
      eprint={2504.07128},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2504.07128}, 
}
```
