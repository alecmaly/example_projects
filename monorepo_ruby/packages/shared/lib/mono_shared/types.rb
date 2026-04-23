module MonoShared
  User = Struct.new(:id, :name)

  module Role
    ADMIN = :admin
    USER  = :user
    GUEST = :guest
  end
end
