// Ambient declaration — mirrors typescript/typings/primordials.d.ts from
// the flat fixture. Exercises `.d.ts` without an import statement (ambient)
// and `declare var` / triple-slash-reference consumption pattern.

declare const primordials: {
    decodeURI: typeof decodeURI;
    encodeURI: typeof encodeURI;
    ObjectKeys: (o: object) => string[];
};
