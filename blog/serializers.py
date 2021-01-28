from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Category, Comment
from account.serializers import UserSerializer

User = get_user_model()


class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=250, required=False)
    slug = serializers.SlugField(required=False)
    content = serializers.CharField(required=False)
    create_at = serializers.DateTimeField(read_only=True, required=False)
    update_at = serializers.DateTimeField(read_only=True, required=False)
    publish_time = serializers.DateTimeField(required=False)
    draft = serializers.BooleanField(required=False)
    image = serializers.ImageField(read_only=True, required=False)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False)
    author_details = UserSerializer(source='author', read_only=True)
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False)

    def validate_slug(self, slug):
        try:
            q = Post.objects.get(slug=slug)
            raise serializers.ValidationError("slug must be uniqe")
        except Post.DoesNotExist:
            return slug

    def create(self, validated_data):
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.content = validated_data.get('content', instance.content)
        instance.publish_time = validated_data.get(
            'publish_time', instance.publish_time)
        instance.draft = validated_data.get('draft', instance.draft)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance


class CommentSerilizer(serializers.ModelSerializer):
    author_detail = UserSerializer(source='author', read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
