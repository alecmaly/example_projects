<?php
// `files` autoload entry — executes on require(composer autoload).
// Exposes namespaced functions consumers can `use function` to import.
namespace Mono\Shared;

function hello(string $msg): string {
    return "hello, $msg";
}
