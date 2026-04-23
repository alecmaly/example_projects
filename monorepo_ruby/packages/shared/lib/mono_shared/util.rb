require_relative "types"

module MonoShared
  module Util
    def self.format_user(u); "#{u.id}:#{u.name}"; end
    def self.hello(msg);     "hello, #{msg}";     end
  end
end
