# AI.Web Slice 37A — Controlled Concept-Authority Schema Runtime Specification

## Status

This increment establishes immutable schema contracts only. It creates no populated registry and no live semantic lookup path.

## Accepted parent

- Repository: `/home/nic/forge`
- Parent HEAD: `5bd8a39b91e7ead06523e7fd0aa3ee057c795f74`
- Parent tree: `16a7708c5ea8b208224bd3ef7a51375c8f980138`
- Parent subject: `Slice 36H bounded bootstrap integration and Slice 36 closeout`

## Exact authority

Slice 37A defines versioned immutable record shapes for:

- concept-authority profile;
- empty registry schema contract;
- provenance reference;
- namespace identity;
- concept identity;
- sense identity;
- controlled lexical reference;
- term-to-concept mapping identity;
- semantic-class identity;
- semantic-relation-family identity;
- semantic-relation-type identity.

The records provide exact identity fields, provenance references, versions, lifecycle states, scope declarations, permitted uses, prohibited uses, and permanent non-authority declarations.

## Zero-population requirement

The Slice 37A schema contract requires all registry entry counts to equal zero. It installs no concept, sense, lexical reference, mapping, semantic class, relation family, relation type, or relation instance.

## Historical boundary

Slice 8 remains preserved at commit `f55c3ff076cbb7e30344a82f51707fbd3997130c`. Slice 37A does not modify, import, supersede, or silently promote the Slice 8 scaffold.

## Prohibited behavior

Slice 37A does not:

- consume raw text;
- consume a Slice 36 structural result;
- perform concept lookup;
- perform term mapping;
- select a concept or sense;
- create CandidateMeaning;
- define predicates or participant roles;
- populate semantic relation edges;
- determine truth or evidence validity;
- read or write memory;
- load WordNet, VerbNet, FrameNet, treebanks, dictionaries, corpora, embeddings, vectors, RAG resources, learned parsers, neural classifiers, or language models;
- register routes;
- invoke tools or actions;
- render or deliver output.

## Permanent rule

Scale is not authority. A large vocabulary, familiar wording, external resource coverage, frequency, resemblance, semantic similarity, or model suggestion cannot create controlled concept authority.
