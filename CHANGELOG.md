# CHANGELOG



## v3.0.0 (2023-11-26)

### Breaking

* feat(new_version_methods): cpd new version methods!

BREAKING CHANGE: new version of CPD! ([`db15f7b`](https://github.com/tradefreq/cpd_strategy/commit/db15f7b7ae8bdaab5d1c6cc229dcdd41648eaa75))

### Feature

* feat(docker-compose): update docker-compose to handle sevices in more manual manner ([`b113803`](https://github.com/tradefreq/cpd_strategy/commit/b1138034dd11b6c0388164fd51d8eabcb6353b96))

* feat(cpd): update strategy file to work with new version ([`12ae34e`](https://github.com/tradefreq/cpd_strategy/commit/12ae34ea5a0849a68b04787663e83da306045f3a))


## v2.7.1 (2023-11-18)

### Fix

* fix(docker-compose): remove worker anchors from docker-compose ([`15f7903`](https://github.com/tradefreq/cpd_strategy/commit/15f79031102286524633b4019627d412c282f4bd))


## v2.7.0 (2023-11-08)

### Feature

* feat(cpd): add rsi sub plot ([`f18d463`](https://github.com/tradefreq/cpd_strategy/commit/f18d4636346eab3b1f6d6c4602477a8287fcc836))


## v2.6.0 (2023-11-06)

### Feature

* feat(cpd_docker-compose): add new env in docker-compose (CONFIRMATION_PIVOT_CANDLES) to handle corresponding var in cpd ([`ecbf0cc`](https://github.com/tradefreq/cpd_strategy/commit/ecbf0cc6f0e93c687d93610bd8252e379f857f41))

### Refactor

* refactor(docker-compose): remove 5m cpd service ([`d2781b3`](https://github.com/tradefreq/cpd_strategy/commit/d2781b3d9dc55665fe2594de4af367a63a7a755d))

* refactor(config): disable rate limit options ([`3601eb6`](https://github.com/tradefreq/cpd_strategy/commit/3601eb6abbc299e8122be444791c20d8f7fbb91c))


## v2.5.0 (2023-11-06)

### Feature

* feat(docker-compose): add 15m and 5m timeframes to cpd as new services ([`20cae3a`](https://github.com/tradefreq/cpd_strategy/commit/20cae3ac4a66cb2a16ad6f99003c455bd79129e6))

* feat(cpd): add and enable short signaling section ([`c382166`](https://github.com/tradefreq/cpd_strategy/commit/c382166627b6983910f89f0d2e1dd7f9aba4d3e0))


## v2.4.0 (2023-11-04)

### Feature

* feat(docker-compose): add 1h timeframe to cpd as a new service ([`acb7128`](https://github.com/tradefreq/cpd_strategy/commit/acb71284188007e47ce2279a1a055731984e2919))


## v2.3.0 (2023-10-28)

### Feature

* feat(config): add ratelimit ([`3509a7e`](https://github.com/tradefreq/cpd_strategy/commit/3509a7eb11b464b71f4f59ced925ea80d7f39045))


## v2.2.0 (2023-10-28)

### Feature

* feat(config): modify webhook url (from plotter to plotter_main) ([`3552ff5`](https://github.com/tradefreq/cpd_strategy/commit/3552ff5a4afde2b3d2e8fe15f34492110057c767))

### Fix

* fix(config): remove ratelimit config ([`6268112`](https://github.com/tradefreq/cpd_strategy/commit/62681126e7c84ec42960db844bb5605fca42493e))


## v2.1.1 (2023-10-27)

### Fix

* fix(cpd_compose): redefine the location of enviroment section from anchor shared script to each service ([`aed1a32`](https://github.com/tradefreq/cpd_strategy/commit/aed1a32a5eddae7f8a6408857c4c99fa6d9aa48d))


## v2.1.0 (2023-10-27)

### Feature

* feat(cpd_config): add rate limit to avoid ddos protection error ([`b4d18f1`](https://github.com/tradefreq/cpd_strategy/commit/b4d18f18926df0189d11a08e0881f53336c199e3))


## v2.0.0 (2023-10-27)

### Breaking

* feat(cpd): refactor cpd strategy codes.

BREAKING CHANGE: remove duplicated files for different timeframes and use enviroment varaible to define timeframe for each service based on one strategy file. ([`e387226`](https://github.com/tradefreq/cpd_strategy/commit/e38722679a47f26a725488a45b68bbe56bd87967))


## v1.7.0 (2023-10-23)

### Feature

* feat(CPD): add and activate weekly and deactive hourly timeframe ([`41e1246`](https://github.com/tradefreq/cpd_strategy/commit/41e12464187084855d86ad6b1ff15347e781e9e5))


## v1.6.0 (2023-10-21)

### Feature

* feat(cpd): Add &#39;send_repetitive_signal&#39; parameter for continuous CPD signal sending, regardless of freshness. ([`cd1ccb4`](https://github.com/tradefreq/cpd_strategy/commit/cd1ccb4167314b36f43701934263eb652b2e6706))


## v1.5.0 (2023-10-18)

### Feature

* feat(cpd): adding divergence confirmation ([`8f38139`](https://github.com/tradefreq/cpd_strategy/commit/8f381394b31f98182d875b8482739a5cdef9dde2))

* feat(shared): seperate common functions in cpd strategy and put them in one file and adding divergence ([`c947f6e`](https://github.com/tradefreq/cpd_strategy/commit/c947f6e350c70c5841a1f61e939001ea0ef1526f))


## v1.4.0 (2023-10-17)

### Feature

* feat(cpd): add cpd for multiple timeframes ([`d376d9a`](https://github.com/tradefreq/cpd_strategy/commit/d376d9a900cd225a39818f3b5395e8b1b638b1ed))


## v1.3.0 (2023-10-16)

### Feature

* feat(cpd): consider high column instead of low column to confirm a range is broken or not ([`93af304`](https://github.com/tradefreq/cpd_strategy/commit/93af3040819044e9cb9d20431be247073ad5a6dd))


## v1.2.0 (2023-10-16)

### Feature

* feat(cpd): check if all candles are below base line ([`b47816f`](https://github.com/tradefreq/cpd_strategy/commit/b47816f003f8d588e8e5248202e78c9daeb998ad))


## v1.1.0 (2023-10-16)

### Feature

* feat(cpd): add strategy_name as a new key to metadata ([`50feb97`](https://github.com/tradefreq/cpd_strategy/commit/50feb973b444ef20b83ee6a2d189566a378415f7))


## v1.0.0 (2023-10-16)

### Breaking

* chore(init): init project (v1)

BREAKING CHANGE: The v1 of cpd doesn&#39;t support divergance. ([`a3f8200`](https://github.com/tradefreq/cpd_strategy/commit/a3f82006abad17b0b638e4f28f80bb962a3a13ed))
