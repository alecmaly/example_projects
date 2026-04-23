<?php
namespace Mono\Shared;

enum Role: string {
    case Admin = 'admin';
    case User  = 'user';
    case Guest = 'guest';
}

const DEFAULT_ROLE = Role::User;
