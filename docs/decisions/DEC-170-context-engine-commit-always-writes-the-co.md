---
type: Decision
id: DEC-170
title: context-engine commit always writes the Co-Authored-By trailer, with the right model where it can tell
actor: owner
decision_status: ACCEPTED
decided: 2026-11-07
session: 2026-11-07a
body_sha: sha256:1f0b691a3ff1e7a6696718e5aa6389a8bd088d621d8ee39842d7979c2dc159ca
---

Make the cli command add the header so it's always there. If you can make it add the right model go ahead, otherwise make it add just Claude and have a cli flag for the model or something? Ask fable if you need design ideas. 

Also ask fable about the article takeaways
