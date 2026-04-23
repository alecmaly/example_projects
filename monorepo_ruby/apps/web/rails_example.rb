# Rails / ActiveRecord framework idioms: model with validations,
# associations, scopes, callbacks; controller inheriting from
# ApplicationController; before_action filters; strong parameters;
# routes-block DSL.
#
# Not expected to `require 'rails'` — this fixture is for static
# analysis of Rails-shaped code.

# --- model ---
class RailsUser < ActiveRecord::Base
  self.table_name = "users"

  has_many :posts, dependent: :destroy
  belongs_to :organization, optional: true

  validates :email, presence: true, uniqueness: true, format: { with: /@/ }
  validates :name, length: { maximum: 128 }

  scope :active,  -> { where(archived_at: nil) }
  scope :recent,  ->(limit = 10) { order(created_at: :desc).limit(limit) }

  before_save :normalize_email
  after_create :send_welcome_email

  def self.find_by_email!(email)
    find_by!(email: email.downcase)
  end

  private

  def normalize_email
    self.email = email.to_s.strip.downcase
  end

  def send_welcome_email
    puts "welcome #{email}"
  end
end

# --- controller ---
class UsersController < ApplicationController
  before_action :authenticate_user!
  before_action :set_user, only: [:show, :update, :destroy]
  skip_before_action :verify_authenticity_token, only: [:create]

  def index
    @users = RailsUser.active.recent(params.fetch(:limit, 10).to_i)
    render json: @users
  end

  def show
    render json: @user
  end

  def create
    @user = RailsUser.new(user_params)
    if @user.save
      render json: @user, status: :created
    else
      render json: { errors: @user.errors }, status: :unprocessable_entity
    end
  end

  def update
    if @user.update(user_params)
      render json: @user
    else
      render json: { errors: @user.errors }, status: :unprocessable_entity
    end
  end

  def destroy
    @user.destroy
    head :no_content
  end

  private

  def set_user
    @user = RailsUser.find(params[:id])
  end

  # Strong parameters.
  def user_params
    params.require(:user).permit(:email, :name, :organization_id)
  end

  def authenticate_user!
    raise "unauthorized" unless request.headers["Authorization"].present?
  end
end

# --- routes DSL (normally lives in config/routes.rb) ---
Rails.application.routes.draw do
  namespace :api do
    resources :users, only: [:index, :show, :create, :update, :destroy] do
      member do
        post :archive
      end
      collection do
        get :search
      end
    end
  end

  root to: "users#index"
end if defined?(Rails)
